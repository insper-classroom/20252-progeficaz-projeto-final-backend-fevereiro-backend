```mermaid
classDiagram
    class User {
        - id : ObjectId
        - username : String
        - email : String
        - password : String
        + register(data: dict) : api_response
        + login(data: dict) : api_response
        + me(current_user) : api_response
    }

    class AuthToken {
        - id : ObjectId
        - user : Reference(User)
        - token_type : String
        - expiration_time : Integer
        - created_at : DateTime
        - used_at : DateTime
        + verify_email(data: dict) : api_response
        + resend_verification(data: dict) : api_response
    }

    class Thread {
        - id : ObjectId
        - author : Reference(User)
        - title : String
        - description : String
        - semester : Integer
        - courses : Array(String)
        - subjects : Array(String)
        - upvotes : Integer
        - downvotes : Integer
        - voted_users : Array(String)
        - created_at : DateTime
        + list_threads(current_user: str) : api_response
        + get_thread_by_id(thread_id: str, current_user: str) : api_response
        + create_thread(data: dict, current_user: str) : api_response
        + update_thread_by_id(thread_id: str, data: dict, current_user: str) : api_response
        + delete_thread_by_id(thread_id: str, current_user: str) : api_response
        + upvote_by_id(obj_id: str, current_user: str, obj_type: Literal["threads","posts"]) : api_response
        + downvote_by_id(obj_id: str, current_user: str, obj_type: Literal["thread","post"]) : api_response
    }

    class Post {
        - id : ObjectId
        - thread : Reference(Thread)
        - author : Reference(User)
        - content : String
        - upvotes : Integer
        - downvotes : Integer
        - voted_users : Array(String)
        - created_at : DateTime
        - pinned : Boolean
        + get_post_by_id(post_id: str, current_user: str) : api_response
        + create_post(thread_id: str, data: dict, current_user: str) : api_response
        + update_post_by_id(post_id: str, data: dict, current_user: str) : api_response
        + delete_post_by_id(post_id: str, current_user: str) : api_response
        + pin_post_by_id(post_id: str, current_user: str) : api_response
        + unpin_post_by_id(post_id: str, current_user: str) : api_response
        + upvote_by_id(obj_id: str, current_user: str, obj_type: Literal["threads","posts"]) : api_response
        + downvote_by_id(obj_id: str, current_user: str, obj_type: Literal["thread","post"]) : api_response
    }

    %% Relações
    User "1" --> "0..*" Thread : author
    User "1" --> "0..*" Post : author
    Thread "1" --> "0..*" Post : thread
