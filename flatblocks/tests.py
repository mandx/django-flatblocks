from django import template
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User
from django import db
from django.utils.translation import ugettext as _, get_language, activate

from flatblocks.models import FlatBlock
from flatblocks import settings


class BasicTests(TestCase):
    urls = 'flatblocks.urls'

    def setUp(self):
        self.testblock = FlatBlock.objects.create(
             slug='block',
             header='HEADER',
             content='CONTENT'
        )
        self.admin = User.objects.create_superuser('admin', 'admin@localhost', 'adminpwd')

    def testURLConf(self):
        # We have to support two different APIs here (1.1 and 1.2)
        def get_tmpl(resp):
            if isinstance(resp.template, list):
                return resp.template[0]
            return resp.template
        self.assertEquals(get_tmpl(self.client.get('/edit/1/')).name, 'admin/login.html')
        self.client.login(username='admin', password='adminpwd')
        self.assertEquals(get_tmpl(self.client.get('/edit/1/')).name, 'flatblocks/edit.html')

    def testCacheReset(self):
        """
        Tests if FlatBlock.save() resets the cache.
        """
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block" 60 %}')
        tpl.render(template.Context({}))
        name = '%sblock' % settings.CACHE_PREFIX
        self.assertNotEquals(None, cache.get(name))
        block = FlatBlock.objects.get(slug='block')
        block.header = 'UPDATED'
        block.save()
        self.assertEquals(None, cache.get(name))

    def testSaveKwargs(self):
        block = FlatBlock(slug='missing')
#        block.slug = 'missing'
        self.assertRaises(ValueError, block.save, force_update=True)
        block = FlatBlock.objects.get(slug='block')
        self.assertRaises(db.IntegrityError, block.save, force_insert=True)


class TagTests(TestCase):
    def setUp(self):
        self.testblock = FlatBlock.objects.create(
             slug='block',
             header='HEADER',
             content='CONTENT'
        )

    def testLoadingTaglib(self):
        """Tests if the taglib defined in this app can be loaded"""
        tpl = template.Template('{% load flatblock_tags %}')
        tpl.render(template.Context({}))

    def testExistingPlain(self):
        tpl = template.Template('{% load flatblock_tags %}{% plain_flatblock "block" %}')
        self.assertEqual(u'CONTENT', tpl.render(template.Context({})).strip())

    def testExistingTemplate(self):
        expected = """<div class="flatblock block-block">

    <h2 class="title">HEADER</h2>

    <div class="content">CONTENT</div>
</div>
"""
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block" %}')
        self.assertEqual(expected, tpl.render(template.Context({})))

    def testUsingMissingTemplate(self):
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block" using "missing_template.html" %}')
        exception = template.TemplateSyntaxError
        self.assertRaises(exception, tpl.render, template.Context({}))

    def testSyntax(self):
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block" %}')
        tpl.render(template.Context({}))
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block" 123 %}')
        tpl.render(template.Context({}))
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block" using "flatblocks/flatblock.html" %}')
        tpl.render(template.Context({}))
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block" 123 using "flatblocks/flatblock.html" %}')
        tpl.render(template.Context({}))

    def testBlockAsVariable(self):
        tpl = template.Template('{% load flatblock_tags %}{% flatblock blockvar %}')
        tpl.render(template.Context({'blockvar': 'block'}))


class AutoCreationTest(TestCase):
    """ Test case for block autcreation """

    def testMissingStaticBlock(self):
        """Tests if a missing block with hardcoded name will be auto-created"""
        expected = """<div class="flatblock block-foo">

    <div class="content">foo</div>
</div>"""
        settings.AUTOCREATE_STATIC_BLOCKS = True
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "foo" %}')
        self.assertEqual(expected, tpl.render(template.Context({})).strip())
        self.assertEqual(FlatBlock.objects.count(), 1)
        self.assertEqual(expected, tpl.render(template.Context({})).strip())
        self.assertEqual(FlatBlock.objects.count(), 1)

    def testNotAutocreatedMissingStaticBlock(self):
        """Tests if a missing block with hardcoded name won't be auto-created if feature is disabled"""
        expected = u""
        settings.AUTOCREATE_STATIC_BLOCKS = False
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block" %}')
        self.assertEqual(expected, tpl.render(template.Context({})).strip())
        self.assertEqual(FlatBlock.objects.filter(slug='block').count(), 0)

    def testMissingVariableBlock(self):
        settings.AUTOCREATE_STATIC_BLOCKS = True
        """Tests if a missing block with variable name will simply return an empty string"""
        tpl = template.Template('{% load flatblock_tags %}{% flatblock name %}')
        self.assertEqual('', tpl.render(template.Context({'name': 'foo'})).strip())


class TagDefaultTests(TestCase):
    def setUp(self):
        self.testblock = FlatBlock.objects.create(
             slug='block_default',
             header='HEADER',
             content='CONTENT_DEFAULT'
        )

    def testTagDefault(self):
        expected = u"""<div class="flatblock block-block_default">

    <h2 class="title">HEADER</h2>

    <div class="content">CONTENT_DEFAULT</div>
</div>"""
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block_default" with-default %}This is the default content{% end_flatblock %}')
        self.assertEqual(expected, tpl.render(template.Context({})).strip())

    def testTagPlainDefault(self):
        tpl = template.Template('{% load flatblock_tags %}{% plain_flatblock "block_default" with-default %}This is the default content{% end_plain_flatblock %}')
        self.assertEqual(u'CONTENT_DEFAULT', tpl.render(template.Context({})).strip())

    def testUsingMissingTemplate(self):
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block_default" using "missing_template.html" with-default %}This is the default content{% end_flatblock %}')
        exception = template.TemplateSyntaxError
        self.assertRaises(exception, tpl.render, template.Context({}))

    def testSyntax(self):
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block_default" with-default %}This is the default content{% end_flatblock %}')
        tpl.render(template.Context({}))
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block_default" 123 with-default %}This is the default content{% end_flatblock %}')
        tpl.render(template.Context({}))
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block_default" using "flatblocks/flatblock.html" with-default %}This is the default content{% end_flatblock %}')
        tpl.render(template.Context({}))
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "block_default" 123 using "flatblocks/flatblock.html" with-default %}This is the default content{% end_flatblock %}')
        tpl.render(template.Context({}))

    def testBlockAsVariable(self):
        tpl = template.Template('{% load flatblock_tags %}{% flatblock blockvar with-default %}This is the default content{% end_flatblock %}')
        tpl.render(template.Context({'blockvar': 'block_default'}))

    def testTagDefault_AutoCreate(self):
        block_content = 'This is the default content of block new1'
        block_slug = 'block_default_new1'
        expected = u"""<div class="flatblock block-%(block_slug)s">

    <div class="content">%(block_content)s</div>
</div>""" % {'block_content': block_content, 'block_slug': block_slug}
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "' + \
                                block_slug + '" with-default %}' + block_content + \
                                '{% end_flatblock %}')

        old_setting = settings.AUTOCREATE_STATIC_BLOCKS
        settings.AUTOCREATE_STATIC_BLOCKS = True

        self.assertEqual(expected, tpl.render(template.Context({})).strip())

        flatblock = FlatBlock.objects.get(slug=block_slug)
        self.assertEqual(flatblock.content, block_content)

        settings.AUTOCREATE_STATIC_BLOCKS = old_setting

    def testTagDefault_AutoCreateWithHeader(self):
        block_header = 'Header of block new3'
        block_content = 'This is the default content of block new3'
        block_slug = 'block_default_new3'
        expected = u"""<div class="flatblock block-%(block_slug)s">

    <h2 class="title">%(block_header)s</h2>

    <div class="content">%(block_content)s</div>
</div>""" % {'block_content': block_content, 'block_slug': block_slug,
             'block_header': block_header}
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "' + \
                                block_slug + '" with-default "' + \
                                block_header + '" %}' + block_content + \
                                '{% end_flatblock %}')

        old_setting = settings.AUTOCREATE_STATIC_BLOCKS
        settings.AUTOCREATE_STATIC_BLOCKS = True

        self.assertEqual(expected, tpl.render(template.Context({})).strip())

        flatblock = FlatBlock.objects.get(slug=block_slug)
        self.assertEqual(flatblock.content, block_content)
        self.assertEqual(flatblock.header, block_header)

        settings.AUTOCREATE_STATIC_BLOCKS = old_setting

    def testTagDefault_AutoCreateWithHeaderAsVar(self):
        block_header = 'Header of block new3'
        block_content = 'This is the default content of block new3'
        block_slug = 'block_default_new3'
        expected = u"""<div class="flatblock block-%(block_slug)s">

    <h2 class="title">%(block_header)s</h2>

    <div class="content">%(block_content)s</div>
</div>""" % {'block_content': block_content, 'block_slug': block_slug,
             'block_header': block_header}
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "' + \
                                block_slug + '" with-default header_var %}' + \
                                block_content + \
                                '{% end_flatblock %}')

        old_setting = settings.AUTOCREATE_STATIC_BLOCKS
        settings.AUTOCREATE_STATIC_BLOCKS = True

        self.assertEqual(expected, tpl.render(template.Context({
            'header_var': block_header, })).strip())

        flatblock = FlatBlock.objects.get(slug=block_slug)
        self.assertEqual(flatblock.content, block_content)
        self.assertEqual(flatblock.header, block_header)

        settings.AUTOCREATE_STATIC_BLOCKS = old_setting

    def testTagDefault_DontAutoCreate(self):
        block_content = 'This is the default content of block new2'
        block_slug = 'block_default_new2'
        expected = u""
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "' + \
                                block_slug + '" with-default %}' + block_content + \
                                '{% end_flatblock %}')

        old_setting = settings.AUTOCREATE_STATIC_BLOCKS
        settings.AUTOCREATE_STATIC_BLOCKS = False

        self.assertEqual(expected, tpl.render(template.Context({})).strip())
        self.assertEqual(FlatBlock.objects.filter(slug=block_slug).count(), 0)

        settings.AUTOCREATE_STATIC_BLOCKS = old_setting

    def testTagDefault_CheckStrictFieldsNoUpdate(self):
        block_header = 'Header of block NEW'
        block_content = 'This is the content of block new'
        block_slug = 'block_default_NEW'

        flatblock = FlatBlock.objects.create(slug=block_slug)

        expected = u"""<div class="flatblock block-%(block_slug)s">

    <h2 class="title">%(block_header)s</h2>

    <div class="content">%(block_content)s</div>
</div>""" % {'block_content': block_content, 'block_slug': block_slug,
             'block_header': block_header}
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "' + \
                                block_slug + '" with-default "' + \
                                block_header + '" %}' + block_content + \
                                '{% end_flatblock %}')

        old_setting_autocreate = settings.AUTOCREATE_STATIC_BLOCKS
        old_setting_strictcheck = settings.STRICT_DEFAULT_CHECK
        old_setting_strictcheckupdate = settings.STRICT_DEFAULT_CHECK_UPDATE
        settings.STRICT_DEFAULT_CHECK = True
        settings.STRICT_DEFAULT_CHECK_UPDATE = False
        settings.AUTOCREATE_STATIC_BLOCKS = False

        self.assertEqual(expected, tpl.render(template.Context({})).strip())

        flatblock = FlatBlock.objects.get(slug=block_slug)
        self.assertEqual(flatblock.content, None)
        self.assertEqual(flatblock.header, None)

        settings.AUTOCREATE_STATIC_BLOCKS = old_setting_autocreate
        settings.STRICT_DEFAULT_CHECK = old_setting_strictcheck
        settings.STRICT_DEFAULT_CHECK_UPDATE = old_setting_strictcheckupdate

    def testTagDefault_CheckStrictFieldsDoUpdate(self):
        block_header = 'Header of block NEW'
        block_content = 'This is the content of block new'
        block_slug = 'block_default_NEW'

        flatblock = FlatBlock.objects.create(slug=block_slug)

        expected = u"""<div class="flatblock block-%(block_slug)s">

    <h2 class="title">%(block_header)s</h2>

    <div class="content">%(block_content)s</div>
</div>""" % {'block_content': block_content, 'block_slug': block_slug,
             'block_header': block_header}
        tpl = template.Template('{% load flatblock_tags %}{% flatblock "' + \
                                block_slug + '" with-default "' + \
                                block_header + '" %}' + block_content + \
                                '{% end_flatblock %}')

        old_setting_autocreate = settings.AUTOCREATE_STATIC_BLOCKS
        old_setting_strictcheck = settings.STRICT_DEFAULT_CHECK
        old_setting_strictcheckupdate = settings.STRICT_DEFAULT_CHECK_UPDATE
        settings.STRICT_DEFAULT_CHECK = True
        settings.STRICT_DEFAULT_CHECK_UPDATE = True
        settings.AUTOCREATE_STATIC_BLOCKS = False

        self.assertEqual(expected, tpl.render(template.Context({})).strip())

        flatblock = FlatBlock.objects.get(slug=block_slug)
        self.assertEqual(flatblock.content, block_content)
        self.assertEqual(flatblock.header, block_header)

        settings.AUTOCREATE_STATIC_BLOCKS = old_setting_autocreate
        settings.STRICT_DEFAULT_CHECK = old_setting_strictcheck
        settings.STRICT_DEFAULT_CHECK_UPDATE = old_setting_strictcheckupdate

class TagDefaultWithModelTranslationTests(TestCase):
    def setUp(self):
        FlatBlock.objects.all().delete()

    def testTagDefaultTranslation_CheckStrictFieldsNoUpdate(self):
        old_lang = get_language()
        activate('es')

        block_header = 'Header of block NEW'
        block_header_translated = _('Header of block NEW')
        block_content = 'This is the content of block new'
        block_content_translated = _('This is the content of block new')
        block_slug = 'block_default_NEW'

        flatblock = FlatBlock.objects.create(slug=block_slug)

        expected = u"""<div class="flatblock block-%(block_slug)s">

    <h2 class="title">%(block_header)s</h2>

    <div class="content">%(block_content)s</div>
</div>""" % {'block_content': block_content_translated,
             'block_slug': block_slug,
             'block_header': block_header_translated, }
        tpl = template.Template('{% load i18n flatblock_tags %}{% flatblock "' + \
                                block_slug + '" with-default _("' + \
                                block_header + '") %}{% trans "' + block_content + \
                                '" %}{% end_flatblock %}')

        old_setting_autocreate = settings.AUTOCREATE_STATIC_BLOCKS
        old_setting_strictcheck = settings.STRICT_DEFAULT_CHECK
        old_setting_strictcheckupdate = settings.STRICT_DEFAULT_CHECK_UPDATE
        settings.STRICT_DEFAULT_CHECK = True
        settings.STRICT_DEFAULT_CHECK_UPDATE = False
        settings.AUTOCREATE_STATIC_BLOCKS = False

        self.assertEqual(expected, tpl.render(template.Context({})).strip())

        flatblock = FlatBlock.objects.get(slug=block_slug)
        self.assertEqual(flatblock.content, None)
        self.assertEqual(flatblock.header, None)

        settings.AUTOCREATE_STATIC_BLOCKS = old_setting_autocreate
        settings.STRICT_DEFAULT_CHECK = old_setting_strictcheck
        settings.STRICT_DEFAULT_CHECK_UPDATE = old_setting_strictcheckupdate
        activate(old_lang)

    def testTagDefaultTranslation_CheckStrictFieldsNoUpdate(self):
        old_lang = get_language()
        activate('es')

        block_header = 'Header of block NEW'
        block_header_translated = _('Header of block NEW')
        block_content = 'This is the content of block new'
        block_content_translated = _('This is the content of block new')
        block_slug = 'block_default_NEW_2'

        flatblock = FlatBlock.objects.create(slug=block_slug)

        expected = u"""<div class="flatblock block-%(block_slug)s">

    <h2 class="title">%(block_header)s</h2>

    <div class="content">%(block_content)s</div>
</div>""" % {'block_content': block_content_translated,
             'block_slug': block_slug,
             'block_header': block_header_translated, }
        tpl = template.Template('{% load i18n flatblock_tags %}{% flatblock "' + \
                                block_slug + '" with-default _("' + \
                                block_header + '") %}{% trans "' + block_content + \
                                '" %}{% end_flatblock %}')

        old_setting_autocreate = settings.AUTOCREATE_STATIC_BLOCKS
        old_setting_strictcheck = settings.STRICT_DEFAULT_CHECK
        old_setting_strictcheckupdate = settings.STRICT_DEFAULT_CHECK_UPDATE
        settings.STRICT_DEFAULT_CHECK = True
        settings.STRICT_DEFAULT_CHECK_UPDATE = True
        settings.AUTOCREATE_STATIC_BLOCKS = False

        self.assertEqual(expected, tpl.render(template.Context({})).strip())

        flatblock = FlatBlock.objects.get(slug=block_slug)
        self.assertEqual(flatblock.content, block_content_translated)
        self.assertEqual(flatblock.header, block_header_translated)

        settings.AUTOCREATE_STATIC_BLOCKS = old_setting_autocreate
        settings.STRICT_DEFAULT_CHECK = old_setting_strictcheck
        settings.STRICT_DEFAULT_CHECK_UPDATE = old_setting_strictcheckupdate
        activate(old_lang)