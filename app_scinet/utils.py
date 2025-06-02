from app_scinet.models.ConversationModel import Conversation


def get_or_create_conversation(user1, user2):
    convo = Conversation.objects.filter(participants=user1).filter(participants=user2).first()
    if convo:
        return convo
    convo = Conversation.objects.create()
    convo.participants.set([user1, user2])
    return convo
