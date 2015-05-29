(function(exports) {

  var UtilizationChart = dre(
    'utilization-chart',
    {
      createdCallback: function() {
        var svg = d3.select(this).append('svg');
        var layers = svg.append('g')
          .attr('class', 'layers');
        var axes = svg.append('g')
          .attr('class', 'axes');
        axes.append('g')
          .attr('class', 'axis axis--x');
        axes.append('g')
          .attr('class', 'axis axis--y');
      },

      attachedCallback: function() {
        // console.log('utilization-chart attached');
        updateSize.call(this);
        var self = this;
        ['data-url', 'data-type', 'data'].forEach(function(attr) {
          if (self.hasAttribute(attr)) {
            var value = self.getAttribute(attr);
            // console.log('attr:', attr, '=', value);
            UtilizationChart.prototype.attributeChangedCallback.call(self, attr, null, value);
          } else {
            // console.warn('no', attr, 'attr');
          }
        });
      },

      detachedCallback: function() {
      },

      attributeChangedCallback: function(attr, prev, value) {
        // console.log('attr changed:', attr, '=', prev, '->', value);
        switch (attr) {
          case 'data-url':
            this.data = null;
            return this.dataUrl = value;
          case 'data-type':
            return this.dataType = value;
          case 'data-values':
            return this.dataValues = value;
          case 'data':
            this.dataUrl = null;
            return this.data = value;

          case 'layer':
          case 'x':
          case 'y':
            return this[attr] = value;

          case 'width':
          case 'height':
            updateSize.call(this);
        }
      },

      loaded: descriptor('loaded'),

      dataUrl: descriptor('dataUrl', {
        attr: 'data-url',
        change: onDataChange
      }),

      dataType: descriptor('dataType', {
        attr: 'data-type',
        change: onDataChange
      }),

      dataValues: descriptor('dataValues', {
        attr: 'data-values',
        parse: dl.accessor,
        change: onDataChange
      }),

      data: descriptor('data', {
        attr: 'data',
        parse: JSON.parse,
        change: onDataChange
      }),

      layer: descriptor('layer', {
        attr: 'layer',
        parse: dl.accessor,
        change: onDataChange
      }),

      x: descriptor('x', {
        attr: 'x',
        parse: dl.accessor,
        change: onDataChange
      }),

      y: descriptor('y', {
        attr: 'y',
        parse: dl.accessor,
        change: onDataChange
      }),

      href: descriptor('href', {
        attr: 'href',
        parse: dl.template
      }),

      interpolate: descriptor('interpolate', {
        attr: 'interpolate',
        change: onDataChange
      }),

      color: descriptor('color', {
        attr: 'color',
        change: onDataChange
      }),

      width: descriptor('width', {
        attr: 'width',
        parse: Number
      }),

      height: descriptor('height', {
        attr: 'height',
        parse: Number
      })
    }
  );

  UtilizationChart.DEFAULT_WIDTH = 800;
  UtilizationChart.DEFAULT_HEIGHT = 160;

  UtilizationChart.FILL = {
    user: d3.scale.category20(),
    project: d3.scale.category20c()
  };

  exports.UtilizationChart = UtilizationChart;

  function onDataChange() {
    // console.log('on data change');
    if (this.__timeout) return false;
    this.__timeout = setTimeout((function() {
      // console.log('timeout!', this);
      delete this.__timeout;
      var url = this.dataUrl;
      if (url) {
        var type = this.dataType || inferUrlType(url);
        if (!type) {
          throw new Error('unable to infer data type for URL: "' + url + '"');
        }
        var load = d3[type];
        if (typeof load !== 'function') {
          throw new Error('invalid data type: "' + type + '"');
        }
        var self = this;
        // console.info('loading:', url, 'as', type, '...');
        load(url, function(error, data) {
          if (error) {
            console.error('error:', error);
            return self.dispatchEvent(new CustomEvent('error', error));
          }
          setData.call(self, data);
          self.dispatchEvent(new CustomEvent('load'));
        });
      } else {
        setData.call(this, this.data);
      }
    }).bind(this), 50);
    return true;
  }

  function render(data) {
    // XXX do stuff
    var svg = d3.select(this)
      .select('svg');

    var _y = this.y;
    var getX = this.x;
    var getY = function(d, i) { return +_y.call(this, d, i); };
    var getLayer = this.layer;

    var color = this.color;
    var fill = UtilizationChart.FILL[color] || d3.scale.category20();

    var ld = dl.unique(data, getLayer).sort(d3.ascending);
    var xd = dl.unique(data, getX).sort(d3.ascending);

    var layers = d3.nest()
      .key(getLayer)
      .key(getX)
      .rollup(function(d) {
        return {
          values: d,
          sum: d3.sum(d, getY)
        };
      })
      .map(data);

    layers = d3.entries(layers)
      .map(function(d) {
        var sample = first(d.value).values[0];
        return {
          key: d.key,
          sample: sample,
          values: xd.map(function(x) {
            return {
              x: x,
              y: d.value[x] ? d.value[x].sum : 0,
              z: d.key
            };
          })
        };
      })
      .sort(function(a, b) {
        return d3.ascending(a.key, b.key);
      });

    var stack = d3.layout.stack()
      .order('default')
      .values(dl.accessor('values'));

    var layer = svg.select('.layers')
      .selectAll('.layer')
      .data(stack(layers));
    layer.exit().remove();

    var enter = layer.enter().append('g')
      .attr('class', 'layer');
    var a = enter.append('a')
    a.append('path');
    a.append('title');

    var width = this.width || UtilizationChart.DEFAULT_WIDTH;
    var height = this.height || UtilizationChart.DEFAULT_HEIGHT;
    var margin = {
      top: 5,
      right: 10,
      bottom: 20,
      left: 40
    };
    var left = margin.left;
    var right = width - margin.right;
    var top = margin.top;
    var bottom = height - margin.bottom;

    var x = d3.scale.ordinal()
      .domain(xd)
      .rangePoints([left, right]);

    var yMax = d3.max(xd, function(x, i) {
      return d3.sum(layers, function(d) { return d.values[i].y; });
    });

    var y = d3.scale.linear()
      .domain([0, yMax])
      .range([bottom, top]);

    var xAxis = d3.svg.axis()
      .scale(x)
      .tickFormat(function(str, i) {
        if (i % 2 === 1) return '';
        return str.substr(5)
          .replace(/\b0/g, '')
          .split('-')
          .join('/');
      })
      .orient('bottom');
    svg.select('.axis--x')
      .attr('transform', 'translate(' + [0, bottom] + ')')
      .call(xAxis);

    var yAxis = d3.svg.axis()
      .scale(y)
      .orient('left');
    svg.select('.axis--y')
      .attr('transform', 'translate(' + [left, 0] + ')')
      .call(yAxis);

    var area = d3.svg.area()
      .interpolate(this.interpolate || 'step-before')
      .x(function(d) { return x(d.x); })
      .y0(function(d) { return y(d.y0); })
      .y1(function(d) { return y(d.y0 + d.y); })

    if (this.href) {
      var href = this.href;
      layer.select('a')
        .attr('xlink:href', function(d) {
          return href(d.sample);
        });
    }

    layer.select('title')
      .text(dl.accessor('key'));

    layer.select('path')
      .attr('fill', function(d) {
        return fill(d.key);
      })
      .attr('d', function(d) {
        return area(d.values);
      });
  }

  function setData(data) {
    // console.log('set data:', data);
    if (typeof this.dataValues === 'function') {
      data = this.dataValues.call(this, data);
      // console.log('values:', data);
    }
    // just set the "private" property so that you can access it with this.data
    this.__data = data;
    this.dispatchEvent(new CustomEvent('data', data));
    render.call(this, data);
    this.dispatchEvent(new CustomEvent('render'));
  }

  function updateSize() {
    var width = +this.getAttribute('width') || UtilizationChart.DEFAULT_WIDTH;
    var height = +this.getAttribute('height') || UtilizationChart.DEFAULT_HEIGHT;
    var svg = d3.select(this)
      .select('svg')
        .attr('viewBox', [0, 0, width, height].join(' '));
  }

  function descriptor(name, desc) {
    var prop = '__' + name;
    if (!desc) desc = {};

    var get = function() {
      return desc.attr
        ? this.hasOwnProperty(prop)
          ? this[prop]
          : this.getAttribute(desc.attr)
        : this[prop];
    };

    var set = function(value) {
      // console.log('set', name, value);
      if (desc.change) {
        var changed = desc.change.call(this, value, name);
        if (changed === false) return false;
      }
      return this[prop] = value;
    };

    return {
      enumerable: !!desc.enumerable,
      get: desc.parse
        ? function() {
          var value = get.call(this);
          return desc.parse.call(this, value, name);
        }
        : get,
      set: desc.validate
        ? function(value) {
          value = desc.validate.call(this, value, name);
          return set.call(this, value);
        }
        : set
    };
  }

  function inferUrlType(url) {
    return url.replace(/\?.*/, '').split('.').pop();
  }

  function dre(name, proto, parent) {
    if (!parent) parent = HTMLElement;
    for (var key in proto) {
      if (typeof proto[key] !== 'object') {
        proto[key] = {value: proto[key]};
      }
    }
    return document.registerElement(name, {
      prototype: Object.create(
        parent.prototype,
        proto
      )
    });
  }

  function first(entries) {
    if (Array.isArray(entries)) return entries[0];
    var keys = Object.keys(entries);
    return keys.length ? entries[keys[0]] : null;
  }

})(this);
