import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from natsort import natsorted
from matplotlib.collections import LineCollection
from matplotlib import colors
plt.style.use('fivethirtyeight')


__all__ = ['GraphPlot']


class GraphPlot:
    """
    Class for customized Graph drawing

    :param g: A networkx graph
    :param vc: vertex colour. Can be a valid matplotlib color string,
               a dictionary with node names as keys and values as
               matplotlib color strings/ floats / RGB  tuple. If floats
               then color will be selected on `colormap`. This parameter is
               overridden by vc_attr
    :param cmap: A valid matplotlib colour map
    :param vc_attr: Name of graph attribute to be used for colors.
                    Attribute values should either be floats or ints
    :param vc_default: Default color of a node. Should be either
                       a valid matplotlib string or RGB tuple.
    :param vc_min: Minimum value for vertex colour. If value is less
                   than this threshold, then value will be reset to this
                   threshold.
    :param vc_max: Maximum value for vertex colour. If value is less
                   than this threshold, then value will be reset to this
                   threshold.
    :param vc_percent_trim: Percentage of values to be ceiled or floored.
                            This will set vc_min and vc_max values based on
                            percentiles. Example, setting to 1 will cause
                            lowest 1 % values to be reset to next
                            largest and values larger than 99 percentile
                            (100-1) to set to 99th percentile.
    :param max_ncolors: Maximum number of colours to use
    :param vs: Vertex size. Should be a integer or float value to set
                            size for all nodes or a dictionary with keys as
                            node name and values as either float ot int.
    :param vs_scale: Multiplier for vs
    :param vs_min: Same as vc_min but for vertex size
    :param vs_max: Same as vc_max but for vertex size
    :param vs_percent_trim: Same as vc_percent_trim but for vertex size
    :param vlw: Vertex line width
    :param v_alpha: Transparency/alpha value for vertices. Should be between
                    0 and 1
    :param ec: Edge colour
    :param elw: Edge line width
    :param e_alpha: Edge transparency/alpha value
    :param texts: Text to be placed on the graph. Should be a dictionary
                  with keys as texts and values as tuple for xy coordinates
    :param texts_fs: Font size for texts
    :param title: Title for the Graph
    :param title_fs: Title font size
    :param label_attr: Node attribute to use to retrieve labels
    :param label_attr_type: Can be either 'legend' or 'centroid'
    :param label_attr_pos: Tuple for xy coords to position start of
                           labels. Only used when `label_attr_type` is
                           'centroid'
    :param label_attr_space: Spacing between labels. Only used when
                             `label_attr_type` is 'centroid'
    :param label_attr_fs: Label font size
    :param save_name: File name for saving figure
    :param fig_size: Figure size. Should be a tuple (width, height)
    :param show_fig: If True then show figure
    :param ax: Matplotlib axis. Draws on this axis rather than create new.
    :param verbose: If True, then prints messages.
    """
    def __init__(self, g: nx.Graph, vc='steelblue', cmap=None,
                 vc_attr=None, vc_default='grey',
                 vc_min=None, vc_max=None, vc_percent_trim=None,
                 max_ncolors=40,
                 vs=2, vs_scale=15,
                 vs_min=None, vs_max=None, vs_percent_trim=0,
                 vlw=0, v_alpha=0.6,
                 ec='k', elw=0.1, e_alpha=0.1,
                 texts=None, texts_fs=20,
                 title=None, title_fs=30,
                 label_attr=None, label_attr_type='centroid',
                 label_attr_pos=(1, 1), label_attr_space=0.05,
                 label_attr_fs=16,
                 save_name=None, fig_size=(5, 5), show_fig=True,
                 ax=None, verbose=False):
        if texts is None:
            texts = []
        self.vertexColor = vc
        self.colormap = cmap
        self.vertexColorAttr = vc_attr
        self.vertexColorDefault = vc_default
        self.vertexColorMin = vc_min
        self.vertexColorMax = vc_max
        self.vertexColorTrimValue = vc_percent_trim
        self.maxNColors = max_ncolors
        self.vertexSize = vs
        self.vertexSizeScale = vs_scale
        self.vertexSizeMin = vs_min
        self.vertexSizeMax = vs_max
        self.vertexSizeTrimValue = vs_percent_trim
        self.vertexLineWidth = vlw
        self.vertexAlpha = v_alpha
        self.edgeColors = ec
        self.edgeLineWidth = elw
        self.edgeAlpha = e_alpha
        self.texts = texts
        self.textFontSize = texts_fs
        self.title = title
        self.titleFontSize = title_fs
        self.labelAttr = label_attr
        self.labelAttrType = label_attr_type
        self.labelAttrPos = label_attr_pos
        self.labelAttrSpace = label_attr_space
        self.labelAttrFontSize = label_attr_fs
        self.saveName = save_name
        self.figSize = fig_size
        self.showFig = show_fig
        self.ax = ax
        self.verbose = verbose

        if self.ax is None:
            if self.verbose is True:
                print('Making a new axis')
            _, self.ax = plt.subplots(1, 1, figsize=self.figSize)

        keep_nodes = []
        for node in g.nodes():
            if 'pos' in g.nodes[node]:
                keep_nodes.append(node)
        self.graph = g.subgraph(keep_nodes)

        self._plot_edges()
        self._set_vertex_color()
        self._set_vertex_size()
        self._plot_nodes()
        self._place_attr_label()
        self._clean()
        self._show_save()

    def __repr__(self):
        return "GraphPlot of %d nodes" % len(self.graph)

    def _get_coords(self, node):
        n = self.graph.node[node]
        return n['pos'][0], n['pos'][1]

    def _plot_edges(self):
        edges = np.array([(self._get_coords(x[0]), self._get_coords(x[1]))
                          for x in self.graph.edges()])
        self.ax.add_collection(LineCollection(edges, colors=self.edgeColors,
                                              linewidths=self.edgeLineWidth,
                                              alpha=self.edgeAlpha, zorder=1))

    def _set_vertex_color(self):
        if isinstance(self.vertexColorDefault, str):
            self.vertexColorDefault = colors.to_rgb(
                        self.vertexColorDefault)
        elif isinstance(self.vertexColorDefault, tuple):
            if len(self.vertexColorDefault) not in [3, 4]:
                print('ERROR: vertex default color \
                       tuple should be in RGB format')
                self.vertexColorDefault = colors.to_rgb('grey')
        else:
            print('ERROR: vertex default color should be \
                   either RGB tuple or a named color')
            self.vertexColorDefault = colors.to_rgb('grey')

        if self.vertexColorAttr is not None:
            self.vertexColor = {}
            for i in self.graph.nodes():
                self.vertexColor[i] = self.graph.node[i][self.vertexColorAttr]
            if len(self.vertexColor) > 0:
                uniq_vals = natsorted(set(self.vertexColor.values()))
                if all(isinstance(x, str) for x in uniq_vals):
                    # If attribute values matplotlib string colors then they
                    # are ignored
                    int_map = {v: n for n, v in enumerate(uniq_vals)}
                    new_vals = {}
                    for k, v in self.vertexColor.items():
                        new_vals[k] = int_map[v]
                    self.vertexColor = new_vals

        if isinstance(self.vertexColor, dict):
            self.vertexColor = dict(self.vertexColor)
            keys = list(self.vertexColor.keys())
            vals = [self.vertexColor[x] for x in keys]
            uniq_vals = natsorted(set(vals))
            # Numpy dtype do not play well with type assertion.
            # following statement should not be merged with previous vals
            vals = np.array(vals)

            if all(np.issubdtype(type(x), np.integer) for x in uniq_vals) or \
               all(np.issubdtype(type(x), np.floating) for x in uniq_vals):

                if self.vertexColorMin is None:
                    if self.vertexColorTrimValue is not None:
                        self.vertexColorMin = np.percentile(
                                vals, self.vertexColorTrimValue)
                    else:
                        self.vertexColorMin = vals.min()
                if self.vertexColorMax is None:
                    if self.vertexColorTrimValue is not None:
                        self.vertexColorMax = np.percentile(
                            vals, 100 - self.vertexColorTrimValue)
                    else:
                        self.vertexColorMax = vals.max()
                for k, v in self.vertexColor.items():
                    if v > self.vertexColorMax:
                        self.vertexColor[k] = self.vertexColorMax
                    elif v < self.vertexColorMin:
                        self.vertexColor[k] = self.vertexColorMin

                # recalc vals
                vals = [self.vertexColor[x] for x in keys]
                uniq_vals = natsorted(set(vals))
                vals = np.array(vals)

                if self.colormap is None:
                    if len(uniq_vals) < 20:
                        self.colormap = 'hls'
                    else:
                        self.colormap = 'magma_r'

                n_vals = min(len(uniq_vals), self.maxNColors)
                palette = sns.color_palette(self.colormap, n_vals)

                new_vals = np.digitize(
                    vals, np.linspace(vals.min(), vals.max()+1, n_vals+1)) - 1
                # -1 is used to make the binned values start from 0
                for k, v in zip(keys, new_vals):
                    self.vertexColor[k] = palette[v]

            elif all(isinstance(x, tuple) for x in uniq_vals):
                if all([len(x) == 3 for x in uniq_vals]) is False:
                    print('ERROR: RGB tuple should of have 3 elements')
                    self.vertexColor = {
                        x: colors.to_rgb(self.vertexColorDefault)
                        for x in self.graph.nodes()}
                else:
                    pass  # Already in RGB
            elif all(isinstance(x, str) for x in uniq_vals):
                self.vertexColor = {k: colors.to_rgb(v)
                                    for k, v in self.vertexColor.items()}
            else:
                print('ERROR: Vertex color dict values should be int/float '
                      'values or RGB tuples')
                self.vertexColor = {x: colors.to_rgb(self.vertexColorDefault)
                                    for x in self.graph.nodes()}
        elif isinstance(self.vertexColor, str):
            self.vertexColor = {x: colors.to_rgb(self.vertexColor)
                                for x in self.graph.nodes()}
        else:
            print('ERROR: Vertex color should be either dict or str type')
            self.vertexColor = {x: colors.to_rgb(self.vertexColorDefault)
                                for x in self.graph.nodes()}

    def _set_vertex_size(self):
        if isinstance(self.vertexSize, dict):
            test_val = self.vertexSize[list(self.vertexSize.keys())[0]]
            if isinstance(test_val, float) or isinstance(test_val, int):
                vals = np.array(list(self.vertexSize.values()))
                if self.vertexSizeMin is None:
                    self.vertexSizeMin = np.percentile(
                        vals, self.vertexSizeTrimValue)
                if self.vertexSizeMax is None:
                    self.vertexSizeMax = np.percentile(
                        vals, 100 - self.vertexSizeTrimValue)
            else:
                print('ERROR: Vertex sizes should be float or int values.')
                print('WARNING: Resetting vertex sizes to 25')
                self.vertexSize = {x: 25 for x in self.graph.nodes()}
        elif isinstance(self.vertexSize, float) or \
                isinstance(self.vertexSize, int):
                self.vertexSize = {x: self.vertexSize
                                   for x in self.graph.nodes()}
        else:
            print('ERROR: Vertex sizes should be float or int values.')
            print('WARNING: Resetting vertex sizes to 25')
            self.vertexSize = {x: 25 for x in self.graph.nodes()}

    def _plot_nodes(self):
        pos, colours, sizes = [], [], []
        min_size = min(self.vertexSize.values())
        for i in self.graph.nodes():
            pos.append(self._get_coords(i))
            if i in self.vertexColor:
                colours.append(self.vertexColor[i])
            else:
                colours.append(colors.to_rgb(self.vertexColorDefault))
            if i in self.vertexSize:
                sizes.append(self.vertexSize[i] * self.vertexSizeScale)
            else:
                sizes.append(min_size * self.vertexSizeScale)
        pos = np.array(pos).T
        self.ax.scatter(pos[0], pos[1], s=sizes, c=colours,
                        lw=self.vertexLineWidth,
                        zorder=2, alpha=self.vertexAlpha)

    def _place_attr_label(self):
        if self.labelAttr is not None and self.labelAttrType == 'legend':
            attrs = {}
            for i in self.graph.nodes():
                if self.labelAttr in self.graph.node[i]:
                    if self.graph.node[i][self.labelAttr] not in attrs:
                        attrs[self.graph.node[i][self.labelAttr]] =  \
                            self.vertexColor[i]
                else:
                    if 'Unknown' not in attrs:
                        attrs['Unknown'] = self.vertexColor[i]
            for n, i in enumerate(attrs):
                self.ax.scatter([self.labelAttrPos[0]],
                                [self.labelAttrPos[1] -
                                    n * self.labelAttrSpace],
                                s=100, c=attrs[i])
                self.ax.text(self.labelAttrPos[0] + self.labelAttrSpace,
                             self.labelAttrPos[1] - n * self.labelAttrSpace,
                             i, fontsize=self.labelAttrFontSize, va='center')
        elif self.labelAttr is not None and self.labelAttrType == 'centroid':
            attrs = {}
            for i in self.graph.nodes():
                if self.labelAttr in self.graph.node[i]:
                    if self.graph.node[i][self.labelAttr] not in attrs:
                        attrs[self.graph.node[i][self.labelAttr]] = []
                    attrs[self.graph.node[i][self.labelAttr]].append(
                        self._get_coords(i))
            for i in attrs:
                x = np.array(attrs[i]).T
                self.ax.text(x[0].mean(), x[1].mean(), i, ha='center',
                             fontsize=self.labelAttrFontSize)
        if self.title is not None:
            self.ax.set_title(self.title, fontsize=self.titleFontSize)
        for i in self.texts:
            self.ax.text(self.texts[i][0], self.texts[i][1], i,
                         fontsize=self.textFontSize, ha='center')

    def _clean(self):
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        for i in ['top', 'bottom', 'left', 'right']:
            self.ax.spines[i].set_visible(False)
        self.ax.grid(False)
        self.ax.figure.patch.set_alpha(0)
        self.ax.patch.set_alpha(0)

    def _show_save(self):
        plt.tight_layout()
        if self.saveName is not None:
            plt.savefig(self.saveName, dpi=200, transparent=True)
        if self.showFig is True:
            plt.show()
