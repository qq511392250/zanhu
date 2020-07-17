#! /usr/bin/python3
# -*- coding:utf-8
# __author__ = '__Levvl__'

from __future__ import unicode_literals
import uuid


from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

@python_2_unicode_compatible
class MessageQuerySet(models.query.QuerySet):

    def get_conversation(self, sender, recipient):
        qs_one = self.filter(sender=sender, recipient=recipient)
        qs_two = self.filter(sender=recipient, recipient=sender)
        return qs_one.union(qs_two).order_by('created_at')

    def get_most_recent_conversation(self, recipient):
        try:
            qs_sent = self.filter(sender=recipient)
            qs_recieved = self.filter(recipient=recipient)
            # 最后一条消息
            qs = qs_sent.union(qs_recieved).latest('created_at')
            if qs.sender == recipient:
                return qs.recipient

            return qs.sender
        except self.model.DoesNotExist:
            return get_user_model().objects.get(username=recipient.username)


@python_2_unicode_compatible
class Message(models.Model):
    """用户间私信"""
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages',
                               blank=True, null=True, on_delete=models.SET_NULL, verbose_name='发送者')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages',
                                  blank=True, null=True, on_delete=models.SET_NULL, verbose_name='接受者')
    message = models.TextField(blank=True, null=True, verbose_name='内容')
    unread = models.BooleanField(default=True, verbose_name='是否未读')

    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间')  # 没有updated_at，私信发送之后不能修改或撤回

    objects = MessageQuerySet.as_manager()

    class Meta:
        verbose_name = '私信'
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)

    def __str__(self):
        return self.message

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()












