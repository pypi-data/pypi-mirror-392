from typing import Annotated, Optional, Union
import nvidiautils
from pydantic import BaseModel, Field, field_serializer, field_validator, TypeAdapter


class NvidiaDriverDockerImageConfig(BaseModel):
    architecture: str
    os: str
    cuda_version: Optional[nvidiautils.CudaVersionWithUpdate] = Field(
        None, alias="cudaVersion"
    )
    driver_version: Optional[nvidiautils.DriverVersion] = Field(
        None, alias="driverVersion"
    )

    @field_serializer("cuda_version")
    @staticmethod
    def ser_cuda_version(value):
        return str(value)

    @field_validator("cuda_version", mode="before")
    @classmethod
    def val_cuda_version(cls, value):
        return nvidiautils.CudaVersionWithUpdate.from_string(value)

    @field_serializer("driver_version")
    @staticmethod
    def ser_driver_version(value):
        return str(value)

    @field_validator("driver_version", mode="before")
    @classmethod
    def val_driver_version(cls, value):
        return nvidiautils.DriverVersion.from_string(value)


class NvidiaDriverDockerImageManifestConfig(BaseModel):
    config: NvidiaDriverDockerImageConfig


class NvidiaDriverDockerImageManifestImages(BaseModel):
    images: list[str]


NvidiaDriverDockerImageManifest = TypeAdapter(
    Annotated[
        Union[
            NvidiaDriverDockerImageManifestConfig, NvidiaDriverDockerImageManifestImages
        ],
        Field(union_mode="left_to_right"),
    ]
)
