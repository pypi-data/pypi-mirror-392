# Modal

Types:

```python
from elicitlabs.types import ModalLearnResponse, ModalQueryResponse
```

Methods:

- <code title="post /v1/modal/learn">client.modal.<a href="./src/elicitlabs/resources/modal.py">learn</a>(\*\*<a href="src/elicitlabs/types/modal_learn_params.py">params</a>) -> <a href="./src/elicitlabs/types/modal_learn_response.py">ModalLearnResponse</a></code>
- <code title="post /v1/modal/query">client.modal.<a href="./src/elicitlabs/resources/modal.py">query</a>(\*\*<a href="src/elicitlabs/types/modal_query_params.py">params</a>) -> <a href="./src/elicitlabs/types/modal_query_response.py">ModalQueryResponse</a></code>

# Users

Types:

```python
from elicitlabs.types import UserCreateOrGetResponse
```

Methods:

- <code title="post /v1/users">client.users.<a href="./src/elicitlabs/resources/users.py">create_or_get</a>(\*\*<a href="src/elicitlabs/types/user_create_or_get_params.py">params</a>) -> <a href="./src/elicitlabs/types/user_create_or_get_response.py">UserCreateOrGetResponse</a></code>

# Data

Types:

```python
from elicitlabs.types import DataIngestResponse
```

Methods:

- <code title="post /v1/data/ingest">client.data.<a href="./src/elicitlabs/resources/data/data.py">ingest</a>(\*\*<a href="src/elicitlabs/types/data_ingest_params.py">params</a>) -> <a href="./src/elicitlabs/types/data_ingest_response.py">DataIngestResponse</a></code>

## Job

Types:

```python
from elicitlabs.types.data import JobRetrieveStatusResponse
```

Methods:

- <code title="post /v1/data/job/status">client.data.job.<a href="./src/elicitlabs/resources/data/job.py">retrieve_status</a>(\*\*<a href="src/elicitlabs/types/data/job_retrieve_status_params.py">params</a>) -> <a href="./src/elicitlabs/types/data/job_retrieve_status_response.py">JobRetrieveStatusResponse</a></code>

# Health

Methods:

- <code title="get /health">client.health.<a href="./src/elicitlabs/resources/health.py">check</a>() -> object</code>

# Auth

## Keys

Types:

```python
from elicitlabs.types.auth import KeyCreateResponse, KeyListResponse, KeyRevokeResponse
```

Methods:

- <code title="post /v1/auth/keys">client.auth.keys.<a href="./src/elicitlabs/resources/auth/keys.py">create</a>(\*\*<a href="src/elicitlabs/types/auth/key_create_params.py">params</a>) -> <a href="./src/elicitlabs/types/auth/key_create_response.py">KeyCreateResponse</a></code>
- <code title="get /v1/auth/keys">client.auth.keys.<a href="./src/elicitlabs/resources/auth/keys.py">list</a>() -> <a href="./src/elicitlabs/types/auth/key_list_response.py">KeyListResponse</a></code>
- <code title="delete /v1/auth/keys/{api_key_id}">client.auth.keys.<a href="./src/elicitlabs/resources/auth/keys.py">revoke</a>(api_key_id) -> <a href="./src/elicitlabs/types/auth/key_revoke_response.py">KeyRevokeResponse</a></code>

# Personas

Types:

```python
from elicitlabs.types import PersonaCreateResponse, PersonaRetrieveResponse, PersonaListResponse
```

Methods:

- <code title="post /v1/personas">client.personas.<a href="./src/elicitlabs/resources/personas.py">create</a>(\*\*<a href="src/elicitlabs/types/persona_create_params.py">params</a>) -> <a href="./src/elicitlabs/types/persona_create_response.py">PersonaCreateResponse</a></code>
- <code title="get /v1/personas/{persona_id}">client.personas.<a href="./src/elicitlabs/resources/personas.py">retrieve</a>(persona_id) -> <a href="./src/elicitlabs/types/persona_retrieve_response.py">PersonaRetrieveResponse</a></code>
- <code title="get /v1/personas">client.personas.<a href="./src/elicitlabs/resources/personas.py">list</a>() -> <a href="./src/elicitlabs/types/persona_list_response.py">PersonaListResponse</a></code>

# Inference

Types:

```python
from elicitlabs.types import (
    InferenceGenerateCompletionResponse,
    InferenceGeneratePersonaChatResponse,
)
```

Methods:

- <code title="post /v1/inference/completion">client.inference.<a href="./src/elicitlabs/resources/inference.py">generate_completion</a>(\*\*<a href="src/elicitlabs/types/inference_generate_completion_params.py">params</a>) -> <a href="./src/elicitlabs/types/inference_generate_completion_response.py">InferenceGenerateCompletionResponse</a></code>
- <code title="post /v1/inference/persona-chat">client.inference.<a href="./src/elicitlabs/resources/inference.py">generate_persona_chat</a>(\*\*<a href="src/elicitlabs/types/inference_generate_persona_chat_params.py">params</a>) -> <a href="./src/elicitlabs/types/inference_generate_persona_chat_response.py">InferenceGeneratePersonaChatResponse</a></code>
