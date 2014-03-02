<%
    import re

    # Convert underscore to camelCase
    under_pat = re.compile(r'_([a-z])')
    def to_camelcase(text):
        return under_pat.sub(lambda x: x.group(1).upper(), text)

    def get_singular(name, capitalize = True):
        retval = name
        if (name[len(name)-1] == 's'):
            retval = name[0:len(name)-1]
        if (capitalize):
            retval = retval.capitalize();
        return retval

    def get_plural(name, capitalize = False):
        retval = name
        if (name[len(name)-1] != 's'):
            if (name[len(name)-1] == 'y'):
                name = name[:len(name)-1] + 'ie'
            retval = name + 's'
        if (capitalize):
            retval = retval.capitalize();
        return retval

    # Camel and capitalize
    def name_for_suffix(name, plural=True):
        namex = name
        if (plural):
            namex = get_plural(name);
        return to_camelcase(namex).capitalize();

    def service_call(name, method, plural=True):
        return '$this->' + entity_name + 'Service->' + method + name_for_suffix(entity_name, plural);

%>
<%def name="get_plural(name, capitalize=False)"><%
retval=name
if (name[len(name)-1] != 's'):
    if (name[len(name)-1] == 'y'):
        name = name[:len(name)-1] + 'ie'
    retval = name + 's'
if (capitalize):
    retval = retval.capitalize();
return retval
%>
</%def>
<%def name="to_camelcase(text, capitalize=False, pluralize=False)"><%
    import re

    # Convert underscore to camelCase
    under_pat = re.compile(r'_([a-z])')
    retval = text
    if (pluralize):
        retval = get_plural(retval, capitalize)
    elif (capitalize):
        retval = retval.capitalize()
    return under_pat.sub(lambda x: x.group(1).upper(), retval)
%>
</%def>
