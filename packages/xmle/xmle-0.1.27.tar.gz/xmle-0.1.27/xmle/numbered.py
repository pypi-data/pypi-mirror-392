
from .elem import Elem
from .uid import uid

class NumberedCaption:
	def __init__(self, kind, level=2, anchor=None):
		self._kind = kind
		self._level = level
		self._anchor = anchor
	def __call__(self, caption, anchor=None, level=None, attrib=None, **extra):
		n = level if level is not None else self._level
		result = Elem("h{}".format(n))
		if anchor is None:
			anchor = self._anchor
		if anchor:
			result.put("a", {
				'name': uid(),
				'reftxt': anchor if isinstance(anchor, str) else caption,
				'class': 'toc',
				'toclevel': '{}'.format(n)
			}, )

		result.put("span", {
				'class': f'xmle_{self._kind.lower().replace(" ","_")}_caption xmle_caption',
				'xmle_caption':self._kind,
		}, tail=caption, text=f"{self._kind}: ")
		return result
