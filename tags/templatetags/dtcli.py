from subprocess import Popen, PIPE

from django.template.loader import find_template, get_template
from django.template.loader_tags import IncludeNode
from django.template.base import TemplateSyntaxError, Library, Node, TextNode,\
    token_kwargs, Variable
from django import template
from django.conf import settings
from django.utils import six

register = template.Library()

class MinifyIncludeNode(IncludeNode):
	def __init__(self, template_type, *args, **kwargs):
		self.template_type = template_type
		super(MinifyIncludeNode, self).__init__(*args, **kwargs)

	def render(self, context):
		result = super(MinifyIncludeNode, self).render(context)

		yuicompressor = Popen(['yuicompressor', '--type=%s' % self.template_type], stdout=PIPE, stdin=PIPE)

		yuicompressor.stdin.write(result)
		yuicompressor.stdin.close()

		return yuicompressor.stdout.read()

@register.tag(name='minify')
def do_minify(parser, token):
	"""
    Loads a template and renders it with the current context. You can pass
    additional context using keyword arguments.

    Example::

        {% include "foo/some_include" %}
        {% include "foo/some_include" with bar="BAZZ!" baz="BING!" %}

    Use the ``only`` argument to exclude the current context when rendering
    the included template::

        {% include "foo/some_include" only %}
        {% include "foo/some_include" with bar="1" only %}
	"""
	bits = token.split_contents()
	if len(bits) < 2:
		raise TemplateSyntaxError("%r tag takes at least one argument: the name of the template to be included." % bits[0])
	options = {}
	remaining_bits = bits[2:]
	template_type = None
	while remaining_bits:
		option = remaining_bits.pop(0)
		if option in options:
			raise TemplateSyntaxError('The %r option was specified more '
                                      'than once.' % option)

		if option == 'with':
			value = token_kwargs(remaining_bits, parser, support_legacy=False)
			if not value:
				raise TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % bits[0])
		elif option == 'only':
			value = True
		elif option[:4] == 'type':
			template_type = option[5:]
			continue
		else:
			raise TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (bits[0], option))
		options[option] = value
	isolated_context = options.get('only', False)
	namemap = options.get('with', {})

	if not template_type:
		template_type = str(bits[1]).replace("'", '').replace('"', '').split('.')[-1]

	return MinifyIncludeNode(template_type, parser.compile_filter(bits[1]), extra_context=namemap,
                       isolated_context=isolated_context)
