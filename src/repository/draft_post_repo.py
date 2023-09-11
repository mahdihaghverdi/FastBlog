from src.repository import BaseRepo, RelatedObjectsRepoMixin
from src.repository.models import DraftPostModel
from src.service.objects import DraftPost


class DraftPostRepo(RelatedObjectsRepoMixin, BaseRepo):
    def __init__(self, session):
        model = DraftPostModel
        object_ = DraftPost
        super().__init__(session, model, object_)
