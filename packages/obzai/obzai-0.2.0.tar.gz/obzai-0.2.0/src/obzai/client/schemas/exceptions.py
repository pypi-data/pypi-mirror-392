# Obz AI - Copyright (C) 2025 Alethia XAI Sp. z o.o.
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.


# ObzClient Exceptions
class ObzClientError(RuntimeError):
    """Raise when Obz Client methods fail."""
    pass


# AuthService Exceptions
class APIKeyNotFoundError(RuntimeError):
    """
    Raised when AuthService cannot properly load API Key
    from an evironment or local .netrc file.
    """
    pass

class APIKeyVerificationError(RuntimeError):
    """
    Raised when API key verification fails due to
    connection with backend issue or server-side error.
    """
    pass

class WrongAPIKey(RuntimeError):
    """
    Raised when provided API key turn out to be not valid.
    """
    pass

class SavingCredentialsFailed(RuntimeError):
    """
    Raised when saving API key fails.
    """
    pass


# ProjectService Exceptions
class ProjectInitError(RuntimeError):
    """
    Raised when a project initialization fails.
    """
    pass


# CacheService Exceptions
class CacheServiceError(RuntimeError):
    """
    Raised within Cache Service.
    """
    pass


# UploadService Exceptions
class UploadServiceError(RuntimeError):
    """
    Raised when within UploadService
    """
    pass





 ### OLD
class CredentialsNotFoundError(RuntimeError):
    """Raised when no API key could be found from env or netrc."""
    pass

class ProjectInitializationError(RuntimeError):
    """Raised when project initialization fails due to backend or validation."""
    pass

class BackendConnectionError(ConnectionError):
    """Raised when backend is unreachable or network error occurs."""
    pass

class RefLogUploadError(RuntimeError):
    """Raised when uploading reference data to the backend wasn't successfull."""
    pass

class LogUploadError(RuntimeError):
    """Raised when uploading log data to the backend wasn't succesfull"""
    pass