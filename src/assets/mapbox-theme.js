/**
 * 自定义绘制的默认样式
 * 测量绘制样式为默认
 * 标绘绘制样式根据属性渲染
 */
export default [
    {
      'id': 'gl-draw-polygon-fill-inactive',
      'type': 'fill',
      'filter': ['all',
        ['==', 'active', 'false'],
        ['==', '$type', 'Polygon'],
        ['!=', 'mode', 'static']
      ],
      /*'paint': {
        'fill-color':'#3bb2d0',
        'fill-outline-color':'#3bb2d0',
        'fill-opacity': 0.1
      }*/
      'paint': {
        'fill-color': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_fill"],
          '#aaaaaa'//'#3bb2d0'
        ],
        'fill-outline-color': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_fill-outline-color"],
          '#aaaaaa'//'#3bb2d0'
        ],
        'fill-opacity': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_fill-opacity"],
          0.1
        ]
      }
    },
    {
      'id': 'gl-draw-polygon-fill-active',
      'type': 'fill',
      'filter': ['all', ['==', 'active', 'true'], ['==', '$type', 'Polygon']],
      'paint': {
        'fill-color':  [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_fill"],
          '#aaaaaa'//'#fbb03b'
        ],
        'fill-outline-color':[
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_fill-outline-color"],
          '#aaaaaa'//'#fbb03b'
        ],
        'fill-opacity': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_fill-opacity"],
          0.1
        ]
      }
    },
    {
      'id': 'gl-draw-polygon-midpoint',
      'type': 'circle',
      'filter': ['all',
        ['==', '$type', 'Point'],
        ['==', 'meta', 'midpoint']],
      'paint': {
        'circle-radius': 3,
        'circle-color': '#aaaaaa'//'#fbb03b'
      }
    },
    {
      'id': 'gl-draw-polygon-stroke-inactive',
      'type': 'line',
      'filter': ['all',
        ['==', 'active', 'false'],
        ['==', '$type', 'Polygon'],
        ['!=', 'mode', 'static']
      ],
      'layout': {
        'line-cap': 'round',
        'line-join': 'round'
      },
      'paint': {
        'line-color':[
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_fill-outline-color"],
          '#aaaaaa'//'#fbb03b'
        ],
        'line-width': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_line-width"],
          2
        ]
      }
    },
    {
      'id': 'gl-draw-polygon-stroke-active',
      'type': 'line',
      'filter': ['all', ['==', 'active', 'true'], ['==', '$type', 'Polygon']],
      'layout': {
        'line-cap': 'round',
        'line-join': 'round'
      },
      'paint': {
        'line-color': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_fill-outline-color"],
          '#aaaaaa'//'#fbb03b'
        ],
        'line-dasharray': [0.2, 2],
        'line-width': 2
      }
    },
  
    //线
    {
      'id': 'gl-draw-line-inactive',
      'type': 'line',
      'filter': ['all',
        ['==', 'active', 'false'],
        ['==', '$type', 'LineString'],
        ['!=', 'mode', 'static']
      ],
      'layout': {
        'line-cap': 'round',
        'line-join': 'round'
      },
      /*'paint': {
        'line-color': '#3bb2d0',
        'line-width': 2
      },*/
      'paint': {
        'line-color': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_line-color"],
          '#3bb2d0'
        ],
        'line-width': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_line-width"],
          2
        ],
        'line-opacity': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_line-opacity"],
          1
        ]
  
      }
    },
    {
      'id': 'gl-draw-line-active',
      'type': 'line',
      'filter': ['all',
        ['==', '$type', 'LineString'],
        ['==', 'active', 'true']
      ],
      'layout': {
        'line-cap': 'round',
        'line-join': 'round'
      },
      'paint': {
        'line-color':[
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_line-color"],
          '#aaaaaa'//'#fbb03b'
        ],
        'line-dasharray': [0.2, 2],
        'line-width': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_line-width"],
          2
        ],
        'line-opacity': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_line-opacity"],
          1
        ]
      }
      /*'paint': {
        'line-color': '#fbb03b',
        'line-dasharray': [0.2, 2],
        'line-width': 2
      }*/
    },
    {
      'id': 'gl-draw-polygon-and-line-vertex-stroke-inactive',
      'type': 'circle',
      'filter': ['all',
        ['==', 'meta', 'vertex'],
        ['==', '$type', 'Point'],
        ['!=', 'mode', 'static']
      ],
      'paint': {
        'circle-radius': 5,
        'circle-color': '#fff'
      }
    },
    {
      'id': 'gl-draw-polygon-and-line-vertex-inactive',
      'type': 'circle',
      'filter': ['all',
        ['==', 'meta', 'vertex'],
        ['==', '$type', 'Point'],
        ['!=', 'mode', 'static']
      ],
      'paint': {
        'circle-radius': 3,
        'circle-color': '#aaaaaa'//'#fbb03b'
      }
    },
    {
      'id': 'gl-draw-point-point-stroke-inactive',
      'type': 'circle',
      'filter': ['all',
        ['==', 'active', 'false'],
        ['==', '$type', 'Point'],
        ['==', 'meta', 'feature'],
        ['!=', 'mode', 'static']
      ],
      'paint': {
        'circle-radius': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['+',['get', "user_circle-radius"],2],
          5
        ],
        'circle-opacity': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_circle-opacity"],
          1
        ],
        'circle-color':[
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_circle-color"],
          '#fff'
        ]
      }
    },
  
    // 点
    {
      'id': 'gl-draw-point-inactive',
      'type': 'circle',
      'filter': ['all',
        ['==', 'active', 'false'],
        ['==', '$type', 'Point'],
        ['==', 'meta', 'feature'],
        ['!=', 'mode', 'static']
      ],
      'paint':{
        'circle-radius': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_circle-radius"],
          3
        ],
        'circle-color':[
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_circle-color"],
          '#3bb2d0'
        ],
        'circle-opacity': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_circle-opacity"],
          1
        ]
      }
  
      /*'paint': {
        'circle-radius': 3,
        'circle-color': '#3bb2d0'
      }*/
    },
    {
      'id': 'gl-draw-point-stroke-active',
      'type': 'circle',
      'filter': ['all',
        ['==', '$type', 'Point'],
        ['==', 'active', 'true'],
        ['!=', 'meta', 'midpoint']
      ],
      'paint': {
        //'circle-radius': 7,
        'circle-radius': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ["+", ['get', "user_circle-radius"], 5],
          7
        ],
        'circle-color':'#fff'
      }
    },
    {
      'id': 'gl-draw-point-active',
      'type': 'circle',
      'filter': ['all',
        ['==', '$type', 'Point'],
        ['!=', 'meta', 'midpoint'],
        ['==', 'active', 'true']],
      'paint':{
        'circle-radius': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ["+", ['get', "user_circle-radius"], 3],
          5
        ],
        'circle-color':[
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_circle-color"],
          '#fbb03b'
        ],
        'circle-opacity': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_circle-opacity"],
          1
        ]
      }
      /*'paint': {
        'circle-radius': 5,
        'circle-color': '#fbb03b'
      }*/
    },
    {
      'id': 'gl-draw-polygon-fill-static',
      'type': 'fill',
      'filter': ['all', ['==', 'mode', 'static'], ['==', '$type', 'Polygon']],
      'paint': {
        'fill-color': '#404040',
        'fill-outline-color': '#404040',
        'fill-opacity': 0.1
      }
    },
    {
      'id': 'gl-draw-polygon-stroke-static',
      'type': 'line',
      'filter': ['all', ['==', 'mode', 'static'], ['==', '$type', 'Polygon']],
      'layout': {
        'line-cap': 'round',
        'line-join': 'round'
      },
      'paint': {
        'line-color': '#404040',
        'line-width': 2
      }
    },
    {
      'id': 'gl-draw-line-static',
      'type': 'line',
      'filter': ['all', ['==', 'mode', 'static'], ['==', '$type', 'LineString']],
      'layout': {
        'line-cap': 'round',
        'line-join': 'round'
      },
      'paint': {
        'line-color': '#404040',
        'line-width': 2
      }
    },
    {
      'id': 'gl-draw-point-static',
      'type': 'circle',
      'filter': ['all', ['==', 'mode', 'static'], ['==', '$type', 'Point']],
      'paint': {
        'circle-radius': 5,
        'circle-color': '#404040',
        'circle-opacity': [
          "case",
          ['==', ['get', "user_isPlotFeature"], true], ['get', "user_circle-opacity"],
          1
        ]
      }
    }
  ];
  