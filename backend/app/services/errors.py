class ServiceError(Exception):
    status_code = 503
    code = "service_unavailable"

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class ModelUnavailable(ServiceError):
    code = "model_unavailable"


class ModelOutputInvalid(ServiceError):
    code = "model_output_invalid"


class ArtifactNotFound(ServiceError):
    status_code = 404
    code = "artifact_not_found"


class ArtifactMalformed(ServiceError):
    code = "artifact_malformed"
