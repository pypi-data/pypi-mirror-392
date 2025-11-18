from chem_eclipse.utils import *
import json
import random
from sklearn.model_selection import train_test_split, KFold
from torch.optim.lr_scheduler import ReduceLROnPlateau, LambdaLR
from chem_eclipse.models.BaseModel import *
from torch import nn, Tensor
from torch.utils.data import DataLoader, TensorDataset
import math
from typing import Any
from torch.nn.utils.rnn import pad_sequence


class TransformerModel(BaseModel):
    def __init__(self, config: dict, vocab: Any, p_args, **kwargs):
        super().__init__(p_args)
        if type(vocab) is tuple or type(vocab) is list:
            self.char_to_i, self.i_to_char = vocab
        else:
            self.char_to_i, self.i_to_char = vocab.vocabulary, vocab.decoder_vocabulary
        self.save_path = kwargs.get("save_path", f"results/TransformerModel/{get_version(p_args)}")
        if self.save_path:
            os.makedirs(self.save_path, exist_ok=True)
        self.pad_id = self.char_to_i["[nop]"]
        self.d_model, n_heads, d_feedforward = config["d_model"], config["n_heads"], config["d_feedforward"]
        dropout = config["dropout"]
        self.embed_dropout = config["embed_dropout"]
        self.warm_up_steps = config["warm_up"]
        n_layers = config["n_layers"]
        smoothing = config["smoothing"]
        self.canon_func = canon_smile_rdkit
        self.max_len = self.args.max_len if "max_len" not in kwargs else kwargs["max_len"]
        self.model_config = config
        self.model_outputs = {"train": [], "val": [], "test": []}
        self.metric_history = {"loss": {"train": [], "val": []}, "char_acc": {"train": [], "val": []},
                               "seq_acc": {"train": [], "val": []}}
        self.final_test_metrics = {}
        self.train_steps = kwargs.get("train_steps", None)
        self.embedding = nn.Embedding(len(self.char_to_i), self.d_model, padding_idx=self.pad_id)
        self.pos_embedding = PositionalEncoding(self.d_model, dropout=dropout, max_len=self.max_len)
        enc_norm = nn.LayerNorm(self.d_model)
        encoder_layer = nn.TransformerEncoderLayer(self.d_model, n_heads, d_feedforward, dropout, batch_first=True,
                                                   norm_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, n_layers, norm=enc_norm, enable_nested_tensor=False)
        dec_norm = nn.LayerNorm(self.d_model)
        decoder_layer = nn.TransformerDecoderLayer(self.d_model, n_heads, d_feedforward, dropout, batch_first=True,
                                                   norm_first=True)
        self.decoder_dropout = nn.Dropout(0.0)
        self.decoder = nn.TransformerDecoder(decoder_layer, n_layers, norm=dec_norm)
        self.linear = nn.Linear(self.d_model, len(self.char_to_i))
        self.loss_fn = nn.CrossEntropyLoss(ignore_index=self.pad_id, label_smoothing=smoothing)
        self.softmax = nn.LogSoftmax(dim=-1)
        self._init_params()

    def smiles_to_smiles_inf(self, smiles, **kwargs):
        num_beams = kwargs.get("num_beams", 8)
        enzyme_data = kwargs.get("enzyme_data")
        tensor_input = kwargs.get("tensor_input", False)
        if enzyme_data and not tensor_input:
            smiles = [s + f">{e}" if e else s for s, e in zip(smiles, enzyme_data)]
        with torch.no_grad():
            self.eval()
            bad_smiles = []
            if not tensor_input:
                enc_smiles = [encode_mol(s, self.char_to_i, self.args, enclose=False) for s in smiles]
                for i, enc in enumerate(enc_smiles):
                    if enc is None:
                        bad_smiles.append(i)
                        print(f"Can't encode", smiles[i])
                enc_smiles = [enc for enc in enc_smiles if enc is not None]
                if len(enc_smiles) == 0:
                    return [[""] for _ in range(len(smiles))], [[float("-inf")] for _ in range(len(smiles))]
                enc_smiles = pad_sequence(enc_smiles, batch_first=True, padding_value=self.pad_id)
            else:
                enc_smiles = smiles
            dataset = TensorDataset(enc_smiles)
            sorted_mols = []
            sorted_lls = []
            batch_size = kwargs.get("batch_size", self.args.batch_size // 2)
            if self.max_len > 500:
                batch_size //= 2
            for batch_i in range(0, len(dataset), batch_size):
                batch = dataset[batch_i: batch_i + batch_size]
                enc_batch = batch[0]
                enc_batch = enc_batch.to(self.device)
                sorted_mols_b, sorted_lls_b, _ = beam_decode(self, enc_batch, num_beams=num_beams)
                sorted_mols.extend(sorted_mols_b)
                sorted_lls.extend(sorted_lls_b)
            sorted_mols = torch.stack(sorted_mols, dim=0).cpu().numpy()
            sorted_lls = torch.stack(sorted_lls, dim=0).cpu().numpy()
            predicted_smiles = []
            predicted_probabilities = []
            for i in range(len(sorted_mols)):
                pred_smiles = []
                pred_probas = []
                for j in range(len(sorted_mols[i])):
                    smiles = decode_mol(sorted_mols[i, j], self.i_to_char, self.canon_func)
                    if len(smiles) > 0:
                        pred_smiles.append(smiles)
                        pred_probas.append(sorted_lls[i, j].astype(float))
                predicted_smiles.append(pred_smiles)
                predicted_probabilities.append(pred_probas)
            for bad_i in bad_smiles:
                predicted_smiles.insert(bad_i, [""])
                predicted_probabilities.insert(bad_i, [float("-inf")])
        return predicted_smiles, predicted_probabilities

    def reset_model(self):
        self.final_test_metrics = {}
        self.model_outputs = {"train": [], "val": [], "test": []}
        self.metric_history = {"loss": {"train": [], "val": []}, "char_acc": {"train": [], "val": []},
                               "seq_acc": {"train": [], "val": []}}
        self._init_params()

    def encode_data(self, smiles, no_mapping_split=False) -> tuple[DataLoader, DataLoader, DataLoader]:
        split_path = os.path.join(self.save_path, "split.json")
        if self.args.split_path and os.path.exists(self.args.split_path):
            split_path = self.args.split_path
        if os.path.exists(split_path):
            with open(split_path) as split_file:
                splits = json.load(split_file)
            train = splits["train"]
            val = splits["val"]
            test = splits["test"]
        else:
            train, val, test = get_data_splits(smiles, seed=self.args.seed)
        with open(os.path.join(self.save_path, "split.json"), "w") as split_file:
            json.dump({"train": train, "val": val, "test": test}, split_file)

        train = encode_reactions(train, self.char_to_i, self.args)
        val = encode_reactions(val, self.char_to_i, self.args)
        test = encode_reactions(test, self.char_to_i, self.args)
        train, val, test = get_loaders(train, val, test, (self.args.batch_size, self.args.batch_size, self.args.batch_size), self.args)
        self.train_steps = math.ceil(len(train) * self.args.epochs)
        return train, val, test

    def encode_data_kfold(self, smiles, extras=None) -> list:
        reactants_set = set([remove_mapping(r.split(">>")[0]) for r in smiles])
        reactants = []
        for s in smiles:
            s = remove_mapping(s.split(">>")[0])
            if s in reactants_set:
                reactants.append(s)
        random.Random(1).shuffle(reactants)
        n_splits = 10
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=1)
        split_loaders = []
        for train_index, val_test_index in kf.split(reactants):
            train_val = [reactants[i] for i in train_index]
            test = [reactants[i] for i in val_test_index]
            train, val = train_test_split(train_val, test_size=len(test), random_state=1)
            train = set(train)
            val = set(val)
            test = set(test)
            train = [r for r in smiles if remove_mapping(r.split(">>")[0]) in train]
            val = [r for r in smiles if remove_mapping(r.split(">>")[0]) in val]
            test = [r for r in smiles if remove_mapping(r.split(">>")[0]) in test]
            train = encode_reactions(train, self.char_to_i, self.args)
            test = encode_reactions(test, self.char_to_i, self.args)
            val = encode_reactions(val, self.char_to_i, self.args)
            split_loaders.append(get_loaders(train, val, test, self.args.batch_size, self.args))
        return split_loaders

    def embed(self, x: Tensor) -> Tensor:
        x = self.embedding(x) * math.sqrt(self.d_model)
        return self.pos_embedding(x)

    def encode(self, src):
        src_mask = torch.eq(src, self.pad_id)
        src = self.embed(src)
        enc_out = self.encoder(src, src_key_padding_mask=src_mask)
        return enc_out, src_mask

    def decode(self, trg, enc_out, src_mask, test=False):
        trg_mask = torch.eq(trg, self.pad_id)
        trg = self.embed(trg)
        trg = self.decoder_dropout(trg)
        square_mask = nn.Transformer.generate_square_subsequent_mask(trg.size(1), device=trg.device)
        square_mask = torch.ne(square_mask, 0.0)
        dec_out = self.decoder(trg, enc_out, tgt_mask=square_mask, tgt_key_padding_mask=trg_mask,
                               memory_key_padding_mask=src_mask)
        output = self.linear(dec_out)
        if test:
            output = self.softmax(output)
        return output

    def forward(self, src: Tensor, trg: Tensor) -> Tensor:
        enc_out, src_mask = self.encode(src)
        output = self.decode(trg, enc_out, src_mask)
        return torch.transpose(output, 1, 2)

    def x_step(self, batch: tuple, step_type: str, save_output: bool = False) -> Tensor:
        x, y = batch
        y_in = y[:, :-1]
        y_out = y[:, 1:]
        model_out = self.forward(x, y_in)
        loss = self.loss_fn(model_out, y_out)
        seq_acc, char_acc = seq_metrics(model_out.detach().argmax(1), y_out, self.pad_id)
        self.log(f"{step_type}_loss", loss.item(), on_step=step_type == "train", logger=True, sync_dist=True,
                 prog_bar=True, batch_size=x.size(0))
        if step_type == "train":
            opt = self.trainer.optimizers[0]
            lr = opt.param_groups[0]["lr"]
            self.log("lr", lr, on_step=True, prog_bar=True, batch_size=1)
        self.log(f"{step_type}_seq_acc", seq_acc, sync_dist=True, prog_bar=True, batch_size=x.size(0))
        self.log(f"{step_type}_char_acc", char_acc, sync_dist=True, prog_bar=True, batch_size=x.size(0))
        self.metric_history["loss"][step_type].append(loss.item())
        self.metric_history["char_acc"][step_type].append(char_acc.item())
        self.metric_history["seq_acc"][step_type].append(seq_acc.item())

        if save_output:
            self.model_outputs[step_type].append([model_out.detach().cpu(), y_out.cpu()])
        return loss

    def test_step(self, batch: tuple, batch_id: int) -> None:
        x, y = batch
        sorted_mols, sorted_lls, sorted_all_lls = beam_decode(self, x, num_beams=2 if self.args.debug else 5)
        self.model_outputs["test"].append((x.cpu(), [sorted_mols.cpu(), y.cpu(), sorted_lls.cpu()]))

    def on_test_epoch_end(self) -> None:
        outputs = self.model_outputs["test"]
        self.final_test_metrics.update(
            process_seq_test_outputs(outputs, self.save_path, self.i_to_char, self.args))

    def _transformer_lr(self, step):
        mult = self.d_model ** -0.5
        step = 1 if step == 0 else step  # Stop div by zero errors
        lr = min(step ** -0.5, step * (self.warm_up_steps ** -1.5))
        return self.model_config["lr"] * mult * lr

    def configure_optimizers(self):
        optimiser = torch.optim.Adam(self.parameters(), lr=self.model_config["lr"],
                                     weight_decay=self.model_config["weight_decay"])
        if self.model_config["scheduler"] == "trans_sch":
            trans_sch = FuncLR(optimiser, lr_lambda=self._transformer_lr)
            sch = {"scheduler": trans_sch, "interval": "step"}
            return [optimiser], [sch]
        elif self.model_config["scheduler"] == "plateau":
            scheduler = ReduceLROnPlateau(optimiser, mode="max", factor=0.2, patience=2)
            return {"optimizer": optimiser, "lr_scheduler": {"scheduler": scheduler, "monitor": "val_seq_acc"}}
        else:
            raise ValueError(f"Unknown lr scheduler: {self.model_config['scheduler']}")


class PositionalEncoding(nn.Module):

    def __init__(self, d_model: int, dropout: float = 0.0, max_len: int = 128):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(1, max_len, d_model)
        pe[0, :, 0::2] = torch.sin(position * div_term)
        pe[0, :, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: Tensor) -> Tensor:
        """
        Arguments:
            x: Tensor, shape ``[batch_size, seq_len, embedding_dim]``
        """
        pe = self.pe[:, :x.size(1), :]
        x = x + pe
        return self.dropout(x)


class FuncLR(LambdaLR):
    def get_lr(self):
        return [lmbda(self.last_epoch) for lmbda in self.lr_lambdas]


def seq_metrics(pred_is: Tensor, y: Tensor, pad_id: int) -> tuple[Tensor, Tensor]:
    pred_is[y == pad_id] = pad_id
    seq_accuracy = torch.eq(pred_is, y)
    seq_accuracy = torch.all(seq_accuracy, 1)
    seq_accuracy = torch.count_nonzero(seq_accuracy) / seq_accuracy.nelement()
    pred_is = pred_is.flatten()
    y = y.flatten()
    char_accuracy = torch.eq(pred_is, y)
    padding = torch.nonzero(torch.eq(y, pad_id))
    char_accuracy[padding] = False
    char_accuracy = torch.count_nonzero(char_accuracy) / (char_accuracy.size(0) - padding.flatten().size(0))
    return seq_accuracy, char_accuracy


def get_version(args):
    version_list = [args.data_name, str(args.seed)]
    if args.enzymes:
        version_list.append("enzymes")
    return "_".join(version_list)
