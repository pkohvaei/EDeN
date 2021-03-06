import networkx as nx
import subprocess as sp

def RNA_MFE_to_eden(input = None, input_type = None, options = dict()):
    """
    Takes a list of strings and yields networkx graphs.

    Parameters
    ----------
    input : string
        A pointer to the data source.

    input_type : ['url','file','list']
        If type is 'url' then 'input' is interpreted as a URL pointing to a file.
        If type is 'file' then 'input' is interpreted as a file name.
        If type is 'list' then 'input' is interpreted as a list of strings.
    """
    input_types = ['url','file','list']
    assert(input_type in input_types),'ERROR: input_type must be one of %s ' % input_types

    if input_type == 'file':
        f = open(input,'r')
    elif input_type == 'url':
        import requests
        f = requests.get(input).text.split('\n')
    elif input_type == "list":
        f = input
    return _RNA_MFE_to_eden(f, options = options)        
   


def RNAfold_wrapper(sequence, options = None):
    defaults = {'path_to_program': 'RNAfold',
    'opt':'--noPS'}
    defaults.update(options)
    cmd = 'echo "%s" | %s %s' % (sequence,defaults['path_to_program'],defaults['opt'])
    out = sp.check_output(cmd, shell = True)
    text = out.strip().split('\n')
    seq_info = text[0]
    seq_struct = text[1].split()[0]
    return seq_info, seq_struct


def string_to_networkx(sequence, options = None):
    seq_info, seq_struct = RNAfold_wrapper(sequence, options)
    G = nx.Graph()
    lifo = list()
    i=0;
    for c,b in zip(seq_info, seq_struct):
        G.add_node(i)
        G.node[i]['label'] = c
        G.node[i]['position'] = i            
        if i > 0:
            G.add_edge(i,i-1)
            G.edge[i][i-1]['label'] = '-'
        if b == '(':
            lifo += [i]
        if b == ')':
            j = lifo.pop()
            G.add_edge(i,j)
            G.edge[i][j]['label'] = '='
        i+=1
    return G


def _RNA_MFE_to_eden(data_str_list, options = None):
    line_buffer = ''
    for line in data_str_list:
        _line = line.strip().upper()
        if _line:
            if _line[0] == '>':
                #extract string from header
                header_str = _line[1:] 
                if len(line_buffer) > 0:
                    G = string_to_networkx(line_buffer, options = options)
                    G.graph['ID'] = prev_header_str
                    yield G
                line_buffer = ''
                prev_header_str = header_str
            else:
                line_buffer += _line
    if len(line_buffer) > 0:
        G = string_to_networkx(line_buffer, options = options)
        G.graph['ID'] = prev_header_str
        yield G