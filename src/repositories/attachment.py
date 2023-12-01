""" Defines the Attachment repository """

from models import Attachment, UserHasAttachment

class AttachmentRepository:
    """ The repository for attachment """

    @staticmethod
    def create_attachment(hash_name):
        attachment = Attachment(hash_name)
        return attachment.save()

    @staticmethod
    def read_attachment(hash_name, user_id=None):
        """ Query attachment using its hash_name """

        # without user restriction
        if not user_id:
            attachment_query = Attachment.query.filter_by(hash_name=hash_name)
            return attachment_query.one() if attachment_query.count() == 1 else None
        
        # with user_id restriction to check allowed access
        attachment_query = Attachment.query\
            .join(UserHasAttachment, Attachment.id == UserHasAttachment.attachment_id)\
            .filter(Attachment.hash_name == hash_name, UserHasAttachment.user_id == user_id)
        return attachment_query.one() if attachment_query.count() == 1 else None