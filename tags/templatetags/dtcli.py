import os.path, sys
from subprocess import Popen, PIPE

from django.template.loader import find_template, get_template
from django.template.loader_tags import IncludeNode
from django.template.base import TemplateSyntaxError, Library, Node, TextNode,\
    token_kwargs, Variable
from django import template
from django.conf import settings
from django.utils import six

register = template.Library()

class LessIncludeNode(IncludeNode):
	def __init__(self, template_type, template_filename, *args, **kwargs):
		self.template_type = template_type
		self.template_filename = template_filename
		super(LessIncludeNode, self).__init__(*args, **kwargs)

	def render(self, context):
		result = super(LessIncludeNode, self).render(context)

		less_directory = os.path.dirname(self.template_filename)

		if self.template_type == 'less':
			self.template_type = 'css'

		yuicompressor = Popen(['yuicompressor', '--type=%s' % self.template_type], stdout=PIPE, stdin=PIPE)
		lessc = Popen(['lessc', '-', '--include-path=.:%s' % less_directory], stdout=yuicompressor.stdin, stdin=PIPE, stderr=PIPE)

		lessc.stdin.write(result)
		lessc.stdin.close()
		
		# this is tu surpress annoying message
		for line in lessc.stderr.readlines():
			if line.startswith('util.print:'):
				continue
			sys.stderr.write(line)

		yuicompressor.stdin.close()

		return yuicompressor.stdout.read()

class MinifyIncludeNode(IncludeNode):
	def __init__(self, template_type, template_filename, *args, **kwargs):
		self.template_type = template_type
		self.template_filename = template_filename
		super(MinifyIncludeNode, self).__init__(*args, **kwargs)

	def render(self, context):
		result = super(MinifyIncludeNode, self).render(context)

		yuicompressor = Popen(['yuicompressor', '--type=%s' % self.template_type], stdout=PIPE, stdin=PIPE)

		yuicompressor.stdin.write(result)
		yuicompressor.stdin.close()

		return yuicompressor.stdout.read()

@register.tag(name='minify')
def do_minify(parser, token):
	return _do_include(parser, token, MinifyIncludeNode)

@register.tag(name='less')
def do_less(parser, token):
	return _do_include(parser, token, LessIncludeNode)

def _do_include(parser, token, _class):
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

	template_filename = str(bits[1]).replace("'", '').replace('"', '')
	if not template_type:
		template_type = template_filename.split('.')[-1]

	return _class(template_type, template_filename, parser.compile_filter(bits[1]), extra_context=namemap,
                       isolated_context=isolated_context)
