# coding: utf-8
from typing import Any, Dict, Optional

from delta_trace_db.query.cause.permission import Permission
from delta_trace_db.query.query import Query
from delta_trace_db.query.transaction_query import TransactionQuery


class UtilQuery:
    """
    (en) Utilities for query processing.

    (ja) クエリ処理用のユーティリティです。
    """

    @staticmethod
    def convert_from_json(src: Dict[str, Any]) -> Query | TransactionQuery:
        """
        (en) Restores a Query or TransactionQuery class from a JSON dict.

        (ja) JSONのdictから、QueryまたはTransactionQueryクラスを復元します。

        Parameters
        ----------
        src: Dict[str, Any]
            The dict of Query or TransactionQuery class.

        Raises
        ------
        ValueError
            Throws on ValueError if you pass an incorrect class.
        """
        try:
            if src.get("className") == "Query":
                return Query.from_dict(src)
            elif src.get("className") == "TransactionQuery":
                return TransactionQuery.from_dict(src)
            else:
                raise ValueError("Unsupported query class")
        except Exception:
            raise ValueError("Unsupported object")

    @staticmethod
    def check_permissions(q: Query, collection_permissions: Optional[Dict[str, Permission]]) -> bool:
        """
        (en) Restores a Query or TransactionQuery class from a JSON dict.

        (ja) JSONのdictから、QueryまたはTransactionQueryクラスを復元します。

        Parameters
        ----------
        q: Query
            The query you want to look up.
        collection_permissions: Optional[Dict[str, Permission]]
            The permissions of the user performing this operation.
            Use null on the frontend, if this is null then everything is allowed.
        """
        if collection_permissions is None:
            return True
        if q.target not in collection_permissions:
            return False

        # allowsのチェック
        p = collection_permissions[q.target]
        if q.type in p.allows:
            return True

        return False
