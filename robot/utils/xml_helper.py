import xml.etree.ElementTree as et

# XML 的补丁, 让 ElementTree 支持 CDATA


def CDATA(text=None):
    element = et.Element('![CDATA[')
    element.text = text
    return element


et._original_serialize_xml = et._serialize_xml


def _serialize_xml(write, elem, qnames, namespaces,short_empty_elements, **kwargs):

    if elem.tag == '![CDATA[':
        write("<%s%s]]>" % (elem.tag, elem.text))
        if elem.tail:
            write(et._escape_cdata(elem.tail))
    else:
        return et._original_serialize_xml(write, elem, qnames, namespaces,short_empty_elements, **kwargs)


et._serialize_xml = et._serialize['xml'] = _serialize_xml
