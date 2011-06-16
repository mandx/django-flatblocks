# -*- coding: utf-8 -*-

from modeltranslation.translator import translator, TranslationOptions

from flatblocks.models import FlatBlock

class FlatBlockTranslationOptions(TranslationOptions):
    fields = ('header', 'content', )
translator.register(FlatBlock, FlatBlockTranslationOptions)
