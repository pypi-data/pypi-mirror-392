from dataclasses import dataclass


@dataclass(order=True, frozen=True)
class DriverVersion:
    x: int
    y: int
    z: int

    @classmethod
    def from_string(cls, s):
        msg = "Malformed driver version"
        parts = s.split(".")
        if len(parts) != 3:
            raise ValueError(msg)
        for i in range(len(parts)):
            try:
                parts[i] = int(parts[i])
            except ValueError:
                raise ValueError(msg) from None
        return cls(*parts)

    def __str__(self):
        return f"{self.x:d}.{self.y:02d}.{self.z:02d}"


@dataclass(order=True, frozen=True)
class CudaVersionWithUpdate:
    major: int
    minor: int
    update: int

    @classmethod
    def from_string(cls, s):
        msg = "Malformed driver version"
        parts = s.split(".")
        if len(parts) != 3:
            raise ValueError(msg)
        for i in range(len(parts)):
            try:
                parts[i] = int(parts[i])
            except ValueError:
                raise ValueError(msg) from None
        return cls(*parts)

    def __str__(self):
        return f"{self.major:d}.{self.minor:d}.{self.update:d}"


@dataclass(frozen=True)
class DriverDockerImageTag:
    version: DriverVersion
    os: str

    @classmethod
    def from_string(cls, s):
        msg = "Malformed driver Docker image tag"
        parts = s.split("-", 1)
        if len(parts) != 2:
            raise ValueError(msg)
        version, os = parts
        try:
            version = DriverVersion.from_string(version)
        except ValueError:
            raise ValueError(msg)
        if not any(os.startswith(e) for e in ("ubuntu", "centos", "rhcos", "rhel")):
            raise ValueError(msg)
        return cls(version, os)

    def __str__(self):
        return f"{self.version!s:s}-{self.os:s}"
