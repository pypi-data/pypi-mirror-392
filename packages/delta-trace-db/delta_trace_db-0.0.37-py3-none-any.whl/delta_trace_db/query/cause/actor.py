from typing import Any, Dict, Optional, override

from file_state_manager import CloneableFile
from file_state_manager.util_object_hash import UtilObjectHash

from delta_trace_db.db.util_copy import UtilCopy
from delta_trace_db.query.cause.enum_actor_type import EnumActorType
from delta_trace_db.query.cause.permission import Permission


# 深いコレクション比較（Dart の DeepCollectionEquality 相当）
def deep_collection_equals(a: Any, b: Any) -> bool:
    """
    (en) Deep collection comparison function (equivalent to Dart's DeepCollectionEquality)

    (ja) 深いコレクション比較用関数（Dart の DeepCollectionEquality 相当）

    Parameters
    ----------
    a: Any
        Comparison object A.
    b: Any
        Comparison object B.
    """
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return False
        return all(deep_collection_equals(a[k], b[k]) for k in a)
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        return all(deep_collection_equals(x, y) for x, y in zip(a, b))
    else:
        return a == b


class Actor(CloneableFile):
    className = "Actor"
    version = "5"

    def __init__(self, actor_type: EnumActorType, actor_id: str,
                 collection_permissions: Optional[Dict[str, Permission]] = None,
                 context: Optional[Dict[str, Any]] = None):
        """
        (en) This class defines the information of the person who
        requested the database operation.

        (ja) データベースの操作をリクエストした者の情報を定義するクラスです。

        Parameters
        ----------
        actor_type: EnumActorType
            The actor type. Choose from HUMAN, AI, or SYSTEM.
        actor_id: str
            The serial id (user id) of the actor.
        collection_permissions: Optional[Dict[str, Permission]]
            Collection-level permissions that relate only to database operations. The key is the collection name.
        context: Optional[Dict[str, Any]]
            The other context.
        """
        super().__init__()
        self.actor_type = actor_type
        self.actor_id = actor_id
        self.collection_permissions = collection_permissions
        self.context = context

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "Actor":
        m_collection_permissions: Optional[Dict[str, Dict[str, Any]]] = None
        if src.get("collectionPermissions") is not None:
            m_collection_permissions = {
                k: v for k, v in src["collectionPermissions"].items()
            }

        collection_permissions: Optional[Dict[str, Permission]] = None
        if m_collection_permissions is not None:
            collection_permissions = {
                key: Permission.from_dict(value)
                for key, value in m_collection_permissions.items()
            }

        return cls(
            actor_type=EnumActorType[src["type"]],
            actor_id=src["id"],
            collection_permissions=collection_permissions,
            context=src.get("context"),
        )

    @override
    def clone(self) -> "Actor":
        return Actor.from_dict(self.to_dict())

    @override
    def to_dict(self) -> Dict[str, Any]:
        m_collection_permissions: Optional[Dict[str, Dict[str, Any]]] = None
        if self.collection_permissions is not None:
            m_collection_permissions = {
                key: value.to_dict()
                for key, value in self.collection_permissions.items()
            }

        return {
            "className": self.className,
            "version": self.version,
            "type": self.actor_type.name,
            "id": self.actor_id,
            "collectionPermissions": m_collection_permissions,
            "context": UtilCopy.jsonable_deep_copy(self.context),
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Actor):
            return False
        return (
                self.actor_type == other.actor_type
                and self.actor_id == other.actor_id
                and deep_collection_equals(
            self.collection_permissions, other.collection_permissions
        )
                and deep_collection_equals(self.context, other.context)
        )

    def __hash__(self) -> int:
        cp_v = 0
        if self.collection_permissions is not None:
            cp_v = UtilObjectHash.calc_map(self.collection_permissions)
        c_v = 0
        if self.context is not None:
            c_v = UtilObjectHash.calc_map(self.context)
        return hash((
            self.actor_type,
            self.actor_id,
            cp_v,
            c_v,
        ))
