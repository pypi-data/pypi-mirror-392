import lightning as L
import abc
from argparse import Namespace
import torch
from torch import nn, Tensor
from torch.utils.data import DataLoader
import os
from chem_eclipse.utils import save_train_metrics


class BaseModel(L.LightningModule, abc.ABC):
    def __init__(self, args: Namespace):
        self.args = args
        self.pre_trained_weights = None
        if args.weights_dataset:
            ckpt_path = f"{args.weights_dataset}/checkpoints/"
            ckpt_path = os.path.join(ckpt_path, [f for f in os.listdir(ckpt_path) if ".ckpt" in f][0])
            if os.path.exists(ckpt_path):
                self.pre_trained_weights = torch.load(ckpt_path)
        super().__init__()

    def _init_params(self):
        """
        Apply Xavier uniform initialisation of learnable weights
        """
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    @abc.abstractmethod
    def encode_data(self, smiles) -> tuple[DataLoader, DataLoader, DataLoader]:
        raise NotImplementedError

    @abc.abstractmethod
    def encode_data_kfold(self, smiles) -> list:
        raise NotImplementedError

    @abc.abstractmethod
    def forward(self, src, trg) -> Tensor:
        raise NotImplementedError

    def on_fit_start(self) -> None:
        # self.trainer.early_stopping_callback.patience = 10
        if self.trainer.early_stopping_callback.mode == "max":
            self.trainer.early_stopping_callback.best_score *= 1e-10
        else:
            self.trainer.early_stopping_callback.best_score *= 1e10
        # if self.pre_trained_weights:
        #     for i, optimizer in enumerate(self.trainer.optimizers):
        #         optimizer.load_state_dict(self.pre_trained_weights["optimizer_states"][i])
        #     for i, lr_scheduler in enumerate(self.trainer.lr_scheduler_configs):
        #         lr_scheduler.scheduler.load_state_dict(self.pre_trained_weights["lr_schedulers"][i])

    @abc.abstractmethod
    def x_step(self, batch: tuple[Tensor, Tensor], step_type: str, save_output: bool = False) -> Tensor:
        raise NotImplementedError

    def training_step(self, batch: tuple[Tensor, Tensor], batch_id: int) -> Tensor:
        return self.x_step(batch, "train")

    def validation_step(self, batch: tuple[Tensor, Tensor], batch_id: int) -> Tensor:
        return self.x_step(batch, "val")

    def on_validation_epoch_end(self) -> None:
        steps_per_epoch = {
            "train": self.trainer.num_training_batches if self.trainer.num_training_batches < float('inf') else 1,
            "val": self.trainer.num_val_batches[0],
            "test": self.trainer.num_val_batches[0]}
        save_train_metrics(self.metric_history, self.save_path, steps_per_epoch)

    @abc.abstractmethod
    def configure_optimizers(self):
        raise NotImplementedError

    @abc.abstractmethod
    def reset_model(self):
        raise NotImplementedError
