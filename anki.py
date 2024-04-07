import genanki
import pandas as pd
from google_speech import Speech
import json
import sqlite3

from urllib.request import urlopen, urlretrieve
import urllib.parse
import re

import time

CHINESE_NOTE_MODEL = genanki.Model(
  1665305021765,
  'ChineseNote',
  fields=[
    {'name': 'Deutsch'},
    {'name': 'Pinyin'},
    {'name': 'Hanzi'},
    {'name': 'Audio'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': """<font style="font-family:SimSun;">{{Hanzi}}</font><br>
{{Pinyin}}<br>
{{Audio}}""",
      'afmt': """<font style="font-family:SimSun;">{{Hanzi}}</font><br>
<div class=lookup>
<a href="https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb={{text:Hanzi}}">MDBG</a><br><br>
</div>
{{Pinyin}}<br><br>
{{Deutsch}}<br>
{{Audio}}"""
    },
    {
      'name': 'Card 2',
      'qfmt': '{{Deutsch}}',
      'afmt': """{{Deutsch}}<br><br>
<font style="font-family:SimSun;">{{Hanzi}}</font>
<div class=lookup>
<a href="https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb={{text:Hanzi}}">MDBG</a><br><br>
</div>
{{Pinyin}}<br>
{{Audio}}"""
    },
  ],
  css=""".card {
 font-family: arial;
 font-size: 30px;
 text-align: center;
 color: black;
 background-color: white;
}

.lookup {font-size: 12px; color:grey;}""")

HANZI_NOTE_MODEL = genanki.Model(
   1704314846730,
   'HanziNote',
   fields=[
      {'name': 'Deutsch'},
      {'name': 'Pinyin'},
      {'name': 'Hanzi'},
      {'name': 'Animation'},
    ],
    templates=[
      {
        'name': 'Card 1',
        'qfmt': """{{Pinyin}}<br>
{{Deutsch}}<br>

<script>
window.AnkiCanvasOptions = {
  frontCanvasSize: 300,
  frontLineWidth: 7,
  backCanvasSize: 300,
  backLineWidth: 7,

  // 'auto' is a special value that will automatically select either 'light' or
  // 'dark' depending on Anki's "Night Mode" status. If you wish to force a
  // colorScheme, you can pass it's name from the colorSchemes settings below.
  colorScheme: 'auto',

  // You can modify the default colorSchemes in the dictionary below, or even
  // add your own colorSchemes beyond light and dark.
  colorSchemes: {
    light: {
      brush: '#000',
      grid: '#dcdcdc',
      gridBg: '#fff',
      buttonIcon: '#464646',
      buttonBg: '#dcdcdc',
      frontBrushColorizer: 'none', // none | spectrum | contrast
      backBrushColorizer: 'spectrum',
    },
    dark: {
      brush: '#fff',
      grid: '#646464',
      gridBg: '#000',
      buttonIcon: '#000',
      buttonBg: '#646464',
      frontBrushColorizer: 'none',
      backBrushColorizer: 'spectrum',
    },
  },
}
</script>
<div id="ac-front"></div>
<script>!function(e){var t={};function n(o){if(t[o])return t[o].exports;var r=t[o]={i:o,l:!1,exports:{}};return e[o].call(r.exports,r,r.exports,n),r.l=!0,r.exports}n.m=e,n.c=t,n.d=function(e,t,o){n.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:o})},n.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.t=function(e,t){if(1&t&&(e=n(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var o=Object.create(null);if(n.r(o),Object.defineProperty(o,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var r in e)n.d(o,r,function(t){return e[t]}.bind(null,r));return o},n.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return n.d(t,"a",t),t},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.p="",n(n.s=12)}([function(e,t,n){"use strict";var o,r,i,s,a;Object.defineProperty(t,"__esModule",{value:!0});const c={frontCanvasSize:300,frontLineWidth:7,backCanvasSize:150,backLineWidth:3.5,colorScheme:"auto",colorSchemes:{light:{brush:"#000",grid:"#dcdcdc",gridBg:"#fff",buttonIcon:"#464646",buttonBg:"#dcdcdc",frontBrushColorizer:"none",backBrushColorizer:"spectrum"},dark:{brush:"#fff",grid:"#646464",gridBg:"#000",buttonIcon:"#000",buttonBg:"#646464",frontBrushColorizer:"none",backBrushColorizer:"spectrum"}}},u=null!=(o=window.devicePixelRatio)?o:2;function l(e){var t;const n=null!=(t=window.AnkiCanvasOptions)?t:{},o=c[e];if(typeof n[e]==typeof o)return n[e]}t.options={frontCanvasSize:(r=l("frontCanvasSize"),null!=r?r:c.frontCanvasSize),frontLineWidth:(i=l("frontLineWidth"),null!=i?i:c.frontLineWidth),backCanvasSize:(s=l("backCanvasSize"),null!=s?s:c.backCanvasSize),backLineWidth:(a=l("backLineWidth"),null!=a?a:c.backLineWidth),colorScheme:function(){var e,t;const n=null!=(e=l("colorScheme"))?e:c.colorScheme,o=function(...e){return e.reduce((e,t)=>{const n=Object.assign({},e);return void 0===t?n:(Object.keys(t).forEach(e=>{var o;n[e]=Object.assign(null!=(o=n[e])?o:{},t[e])}),n)},{})}(c.colorSchemes,l("colorSchemes")),r=document.getElementsByClassName("night_mode").length>0?o.dark:o.light;return null!=(t=o[n])?t:r},hdpiFactor:u}},function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});const o=n(8),r=n(9),i=o._iso(),s=r.defaultStorage();function a(e){s.setItem("state",r.dump(e))}function c(){const e={lines:[],drawing:[],dirty:!0,down:!1};return a(e),i.wrap(e)}function u(e,t){const n=i.unwrap(e);n.down&&(n.drawing.push(t),n.dirty=!0,a(n))}t.saveunsafe=function(e){s.setItem("state",r.dump(e))},t.load=function(){const e=s.getItem("state");return null==e?c():i.wrap(Object.assign(Object.assign({},r.parse(e)),{dirty:!0}))},t.empty=c,t.map=function(e,t){const n=i.unwrap(e),o=r.parse(r.dump(n));return o.lines=o.lines.map(e=>e.map(t)),i.wrap(o)},t.undo=function(e){const t=i.unwrap(e);t.lines.splice(-1,1),t.dirty=!0,a(t)},t.clear=function(e){const t=i.unwrap(e);t.lines.splice(0,t.lines.length),t.dirty=!0,a(t)},t.addDrawingPoint=u,t.addFirstDrawingPoint=function(e,t){i.unwrap(e).down=!0,u(e,t)},t.addLastDrawingPoing=function(e,t){const n=i.unwrap(e);n.drawing.push(t),n.lines.push(n.drawing),n.drawing=[],n.dirty=!0,n.down=!1,a(n)},t.willdisplay=function(e,t){const n=i.unwrap(e);if(n.dirty){const e=t([...n.lines,n.drawing].filter(e=>e.length>0));n.dirty=!e}}},function(e,t,n){var o=n(3),r=n(4),i="undefined"==typeof window?n(6):window,s=i.document,a=i.Text;function c(){var e=[];function t(){var t=[].slice.call(arguments),n=null;function i(t){var c,d,f;if(null==t);else if("string"==typeof t)n?n.appendChild(c=s.createTextNode(t)):(f=o(t,/([\\.#]?[^\\s#.]+)/),/^\\.|#/.test(f[1])&&(n=s.createElement("div")),l(f,(function(e){var t=e.substring(1,e.length);e&&(n?"."===e[0]?r(n).add(t):"#"===e[0]&&n.setAttribute("id",t):n=s.createElement(e))})));else if("number"==typeof t||"boolean"==typeof t||t instanceof Date||t instanceof RegExp)n.appendChild(c=s.createTextNode(t.toString()));else if(d=t,"[object Array]"==Object.prototype.toString.call(d))l(t,i);else if(u(t))n.appendChild(c=t);else if(t instanceof a)n.appendChild(c=t);else if("object"==typeof t)for(var p in t)if("function"==typeof t[p])/^on\\w+/.test(p)?function(t,o){n.addEventListener?(n.addEventListener(t.substring(2),o[t],!1),e.push((function(){n.removeEventListener(t.substring(2),o[t],!1)}))):(n.attachEvent(t,o[t]),e.push((function(){n.detachEvent(t,o[t])})))}(p,t):(n[p]=t[p](),e.push(t[p]((function(e){n[p]=e}))));else if("style"===p)if("string"==typeof t[p])n.style.cssText=t[p];else for(var h in t[p])!function(o,r){if("function"==typeof r)n.style.setProperty(o,r()),e.push(r((function(e){n.style.setProperty(o,e)})));else var i=t[p][o].match(/(.*)\\W+!important\\W*$/);i?n.style.setProperty(o,i[1],"important"):n.style.setProperty(o,t[p][o])}(h,t[p][h]);else if("attrs"===p)for(var g in t[p])n.setAttribute(g,t[p][g]);else"data-"===p.substr(0,5)?n.setAttribute(p,t[p]):n[p]=t[p];else if("function"==typeof t){g=t();n.appendChild(c=u(g)?g:s.createTextNode(g)),e.push(t((function(e){u(e)&&c.parentElement?(c.parentElement.replaceChild(e,c),c=e):c.textContent=e})))}return c}for(;t.length;)i(t.shift());return n}return t.cleanup=function(){for(var t=0;t<e.length;t++)e[t]();e.length=0},t}function u(e){return e&&e.nodeName&&e.nodeType}function l(e,t){if(e.forEach)return e.forEach(t);for(var n=0;n<e.length;n++)t(e[n],n)}(e.exports=c()).context=c},function(e,t){var n,o,r;
/*!
 * Cross-Browser Split 1.1.1
 * Copyright 2007-2012 Steven Levithan <stevenlevithan.com>
 * Available under the MIT License
 * ECMAScript compliant, uniform cross-browser split method
 */
e.exports=(o=String.prototype.split,r=/()??/.exec("")[1]===n,function(e,t,i){if("[object RegExp]"!==Object.prototype.toString.call(t))return o.call(e,t,i);var s,a,c,u,l=[],d=(t.ignoreCase?"i":"")+(t.multiline?"m":"")+(t.extended?"x":"")+(t.sticky?"y":""),f=0;for(t=new RegExp(t.source,d+"g"),e+="",r||(s=new RegExp("^"+t.source+"$(?!\\s)",d)),i=i===n?-1>>>0:i>>>0;(a=t.exec(e))&&!((c=a.index+a[0].length)>f&&(l.push(e.slice(f,a.index)),!r&&a.length>1&&a[0].replace(s,(function(){for(var e=1;e<arguments.length-2;e++)arguments[e]===n&&(a[e]=n)})),a.length>1&&a.index<e.length&&Array.prototype.push.apply(l,a.slice(1)),u=a[0].length,f=c,l.length>=i));)t.lastIndex===a.index&&t.lastIndex++;return f===e.length?!u&&t.test("")||l.push(""):l.push(e.slice(f)),l.length>i?l.slice(0,i):l})},function(e,t,n){var o=n(5);function r(e){return!!e}e.exports=function(e){var t=e.classList;if(t)return t;var n={add:i,remove:s,contains:a,toggle:function(e){return a(e)?(s(e),!1):(i(e),!0)},toString:function(){return e.className},length:0,item:function(e){return c()[e]||null}};return n;function i(e){var t=c();o(t,e)>-1||(t.push(e),u(t))}function s(e){var t=c(),n=o(t,e);-1!==n&&(t.splice(n,1),u(t))}function a(e){return o(c(),e)>-1}function c(){return function(e,t){for(var n=[],o=0;o<e.length;o++)t(e[o])&&n.push(e[o]);return n}(e.className.split(" "),r)}function u(t){var o=t.length;e.className=t.join(" "),n.length=o;for(var r=0;r<t.length;r++)n[r]=t[r];delete t[o]}}},function(e,t){var n=[].indexOf;e.exports=function(e,t){if(n)return e.indexOf(t);for(var o=0;o<e.length;++o)if(e[o]===t)return o;return-1}},function(e,t){},function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});const o=n(1),r={lineWidth:18};t.rendercanvas=function(e,t,n){o.willdisplay(t,t=>{const o=e.getContext("2d");if(null===o)return!1;const i=Object.assign(Object.assign({},r),n);o.clearRect(0,0,e.width,e.height),function(e,t,n,o){const r=t/2,i=n/2,s=[[0,0,t,n],[t,0,0,n],[r,0,r,n],[0,i,t,i]];e.save();for(let r=0;r<s.length;r++){const i=s[r];e.beginPath(),e.setLineDash([t/80,n/80]),e.strokeStyle=o.grid,e.lineWidth=1,e.moveTo(i[0],i[1]),e.lineTo(i[2],i[3]),e.stroke()}e.restore()}(o,e.width,e.height,i.colorScheme),o.save(),o.lineWidth=i.lineWidth,o.lineCap="round",o.lineJoin="round";for(let e=0;e<t.length;e++){o.beginPath(),o.strokeStyle=i.colorizer(e,t.length);const n=t[e];for(let e=1;e<n.length;e++){const t=n[e-1],r=n[e];o.moveTo(t.x,t.y),o.lineTo(r.x,r.y)}o.stroke()}return o.restore(),!0})},t.renderdom=function(e,t){const n=document.getElementById(e);null!==n&&(null!==n.firstChild&&n.removeChild(n.firstChild),n.appendChild(t))}},function(e,t,n){"use strict";function o(e){return e}Object.defineProperty(t,"__esModule",{value:!0}),t._iso=()=>({unwrap:o,wrap:o})},function(e,t,n){"use strict";var o;Object.defineProperty(t,"__esModule",{value:!0}),window.db=null!=(o=window.db)?o:{};const r=window.db;function i(e){return r[e]}function s(e,t){r[e]=t}t.defaultStorage=function(){var e;return navigator.userAgent.includes("QtWebEngine")?{setItem:s,getItem:i}:null!=(e=window.localStorage)?e:window.sessionStorage},t.dump=JSON.stringify,t.parse=JSON.parse},function(e,t,n){"use strict";function o(e){return"#"+[e.r,e.g,e.b].map(e=>{const t=e.toString(16);return 1===t.length?"0"+t:t}).join("")}function r(e){let t=0,n=0,o=0;const r=e.s,i=e.v,s=e.h,a=Math.floor(6*s),c=6*s-a,u=i*(1-r),l=i*(1-c*r),d=i*(1-(1-c)*r);switch(a%6){case 0:t=i,n=d,o=u;break;case 1:t=l,n=i,o=u;break;case 2:t=u,n=i,o=d;break;case 3:t=u,n=l,o=i;break;case 4:t=d,n=u,o=i;break;case 5:t=i,n=u,o=l}return{r:Math.floor(255*t),g:Math.floor(255*n),b:Math.floor(255*o)}}function i(e,t,n=.95,i=.75){return o(r({h:e/t,s:n,v:i}))}function s(e,t,n=.95,i=.75){return o(r({h:e/.618033988749895,s:n,v:i}))}Object.defineProperty(t,"__esModule",{value:!0}),t.spectrum=i,t.contrast=s,t.none=e=>(t,n)=>e.brush,t.getColorizer=function(e,n){switch(n){case"none":return t.none(e);case"spectrum":return i;case"contrast":return s}}},function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});const o=n(0);t.canvas=e=>({height:`${o.options.frontCanvasSize}px`,width:`${o.options.frontCanvasSize}px`,border:`2px solid ${e.grid}`,background:e.gridBg}),t.result=e=>({display:"inline-block",height:`${o.options.backCanvasSize}px`,width:`${o.options.backCanvasSize}px`,border:`1px solid ${e.grid}`,background:e.gridBg}),t.wrapper=e=>({"text-align":"center"}),t.actions=e=>({}),t.action=e=>({"font-size":"22px",border:"none","border-radius":"50%",outline:"none",background:e.buttonBg,color:e.buttonIcon,display:"inline-flex",width:"44px",height:"44px",padding:"0","align-items":"center","justify-content":"center",margin:"0 5px"})},function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});const o=n(0),r=n(2),i=n(7),s=n(1),a=n(10),c=n(11),u=n(13);requestAnimationFrame((function(){const e=r.context(),t=o.options.colorScheme(),n=e("canvas",{style:c.canvas(t),width:o.options.frontCanvasSize*o.options.hdpiFactor,height:o.options.frontCanvasSize*o.options.hdpiFactor}),l={undo:e("button",{style:c.action(t)}),clear:e("button",{style:c.action(t)})},d=e("div",{style:c.actions(t)},Object.values(l)),f=e("div",{style:c.wrapper(t)},[n,d]);i.renderdom("ac-front",f);const p=s.empty();[["touchstart",s.addFirstDrawingPoint],["touchmove",s.addDrawingPoint],["touchend",s.addLastDrawingPoing],["mousedown",s.addFirstDrawingPoint],["mousemove",s.addDrawingPoint],["mouseup",s.addLastDrawingPoing]].forEach(e=>{n.addEventListener(e[0],((e,t,n)=>r=>{if(r.preventDefault(),!(r instanceof TouchEvent||r instanceof MouseEvent))return;const i=r instanceof TouchEvent?r.changedTouches[0]:r,s={x:(i.pageX-e.offsetLeft)*o.options.hdpiFactor,y:(i.pageY-e.offsetTop)*o.options.hdpiFactor};n(t,s)})(n,p,e[1]),!1)}),function e(){i.rendercanvas(n,p,{colorizer:a.getColorizer(t,t.frontBrushColorizer),lineWidth:o.options.frontLineWidth*o.options.hdpiFactor,colorScheme:t}),requestAnimationFrame(e)}(),n.addEventListener("click",e=>e.preventDefault(),!1),l.undo.addEventListener("click",()=>s.undo(p),!1),l.clear.addEventListener("click",()=>s.clear(p),!1),l.undo.innerHTML=u.undo,l.clear.innerHTML=u.clear}))},function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),t.undo='<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M0 0h24v24H0z" fill="none"/><path d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z" fill="currentColor"/></svg>',t.clear='<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z" fill="currentColor"/><path d="M0 0h24v24H0z" fill="none"/></svg>'}]);</script>""",
        'afmt': """<font style="font-family:SimSun;">{{Hanzi}}</font><br>
<div class=lookup>
<a href="https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb={{text:Hanzi}}">MDBG</a><br><br>
</div>
{{Pinyin}}<br>
{{Deutsch}}<br>
<script>
window.AnkiCanvasOptions = {
  frontCanvasSize: 300,
  frontLineWidth: 7,
  backCanvasSize: 300,
  backLineWidth: 7	,

  // 'auto' is a special value that will automatically select either 'light' or
  // 'dark' depending on Anki's "Night Mode" status. If you wish to force a
  // colorScheme, you can pass it's name from the colorSchemes settings below.
  colorScheme: 'auto',

  // You can modify the default colorSchemes in the dictionary below, or even
  // add your own colorSchemes beyond light and dark.
  colorSchemes: {
    light: {
      brush: '#000',
      grid: '#dcdcdc',
      gridBg: '#fff',
      buttonIcon: '#464646',
      buttonBg: '#dcdcdc',
      frontBrushColorizer: 'none', // none | spectrum | contrast
      backBrushColorizer: 'spectrum',
    },
    dark: {
      brush: '#fff',
      grid: '#646464',
      gridBg: '#000',
      buttonIcon: '#000',
      buttonBg: '#646464',
      frontBrushColorizer: 'none',
      backBrushColorizer: 'spectrum',
    },
  },
}
</script>

<div id="ac-back"></div>
{{Animation}}<br>

<script>!function(e){var t={};function n(r){if(t[r])return t[r].exports;var o=t[r]={i:r,l:!1,exports:{}};return e[r].call(o.exports,o,o.exports,n),o.l=!0,o.exports}n.m=e,n.c=t,n.d=function(e,t,r){n.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:r})},n.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.t=function(e,t){if(1&t&&(e=n(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var r=Object.create(null);if(n.r(r),Object.defineProperty(r,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var o in e)n.d(r,o,function(t){return e[t]}.bind(null,o));return r},n.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return n.d(t,"a",t),t},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.p="",n(n.s=14)}([function(e,t,n){"use strict";var r,o,i,s,c;Object.defineProperty(t,"__esModule",{value:!0});const a={frontCanvasSize:300,frontLineWidth:7,backCanvasSize:150,backLineWidth:3.5,colorScheme:"auto",colorSchemes:{light:{brush:"#000",grid:"#dcdcdc",gridBg:"#fff",buttonIcon:"#464646",buttonBg:"#dcdcdc",frontBrushColorizer:"none",backBrushColorizer:"spectrum"},dark:{brush:"#fff",grid:"#646464",gridBg:"#000",buttonIcon:"#000",buttonBg:"#646464",frontBrushColorizer:"none",backBrushColorizer:"spectrum"}}},u=null!=(r=window.devicePixelRatio)?r:2;function l(e){var t;const n=null!=(t=window.AnkiCanvasOptions)?t:{},r=a[e];if(typeof n[e]==typeof r)return n[e]}t.options={frontCanvasSize:(o=l("frontCanvasSize"),null!=o?o:a.frontCanvasSize),frontLineWidth:(i=l("frontLineWidth"),null!=i?i:a.frontLineWidth),backCanvasSize:(s=l("backCanvasSize"),null!=s?s:a.backCanvasSize),backLineWidth:(c=l("backLineWidth"),null!=c?c:a.backLineWidth),colorScheme:function(){var e,t;const n=null!=(e=l("colorScheme"))?e:a.colorScheme,r=function(...e){return e.reduce((e,t)=>{const n=Object.assign({},e);return void 0===t?n:(Object.keys(t).forEach(e=>{var r;n[e]=Object.assign(null!=(r=n[e])?r:{},t[e])}),n)},{})}(a.colorSchemes,l("colorSchemes")),o=document.getElementsByClassName("night_mode").length>0?r.dark:r.light;return null!=(t=r[n])?t:o},hdpiFactor:u}},function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});const r=n(8),o=n(9),i=r._iso(),s=o.defaultStorage();function c(e){s.setItem("state",o.dump(e))}function a(){const e={lines:[],drawing:[],dirty:!0,down:!1};return c(e),i.wrap(e)}function u(e,t){const n=i.unwrap(e);n.down&&(n.drawing.push(t),n.dirty=!0,c(n))}t.saveunsafe=function(e){s.setItem("state",o.dump(e))},t.load=function(){const e=s.getItem("state");return null==e?a():i.wrap(Object.assign(Object.assign({},o.parse(e)),{dirty:!0}))},t.empty=a,t.map=function(e,t){const n=i.unwrap(e),r=o.parse(o.dump(n));return r.lines=r.lines.map(e=>e.map(t)),i.wrap(r)},t.undo=function(e){const t=i.unwrap(e);t.lines.splice(-1,1),t.dirty=!0,c(t)},t.clear=function(e){const t=i.unwrap(e);t.lines.splice(0,t.lines.length),t.dirty=!0,c(t)},t.addDrawingPoint=u,t.addFirstDrawingPoint=function(e,t){i.unwrap(e).down=!0,u(e,t)},t.addLastDrawingPoing=function(e,t){const n=i.unwrap(e);n.drawing.push(t),n.lines.push(n.drawing),n.drawing=[],n.dirty=!0,n.down=!1,c(n)},t.willdisplay=function(e,t){const n=i.unwrap(e);if(n.dirty){const e=t([...n.lines,n.drawing].filter(e=>e.length>0));n.dirty=!e}}},function(e,t,n){var r=n(3),o=n(4),i="undefined"==typeof window?n(6):window,s=i.document,c=i.Text;function a(){var e=[];function t(){var t=[].slice.call(arguments),n=null;function i(t){var a,d,f;if(null==t);else if("string"==typeof t)n?n.appendChild(a=s.createTextNode(t)):(f=r(t,/([\\.#]?[^\\s#.]+)/),/^\\.|#/.test(f[1])&&(n=s.createElement("div")),l(f,(function(e){var t=e.substring(1,e.length);e&&(n?"."===e[0]?o(n).add(t):"#"===e[0]&&n.setAttribute("id",t):n=s.createElement(e))})));else if("number"==typeof t||"boolean"==typeof t||t instanceof Date||t instanceof RegExp)n.appendChild(a=s.createTextNode(t.toString()));else if(d=t,"[object Array]"==Object.prototype.toString.call(d))l(t,i);else if(u(t))n.appendChild(a=t);else if(t instanceof c)n.appendChild(a=t);else if("object"==typeof t)for(var p in t)if("function"==typeof t[p])/^on\\w+/.test(p)?function(t,r){n.addEventListener?(n.addEventListener(t.substring(2),r[t],!1),e.push((function(){n.removeEventListener(t.substring(2),r[t],!1)}))):(n.attachEvent(t,r[t]),e.push((function(){n.detachEvent(t,r[t])})))}(p,t):(n[p]=t[p](),e.push(t[p]((function(e){n[p]=e}))));else if("style"===p)if("string"==typeof t[p])n.style.cssText=t[p];else for(var h in t[p])!function(r,o){if("function"==typeof o)n.style.setProperty(r,o()),e.push(o((function(e){n.style.setProperty(r,e)})));else var i=t[p][r].match(/(.*)\\W+!important\\W*$/);i?n.style.setProperty(r,i[1],"important"):n.style.setProperty(r,t[p][r])}(h,t[p][h]);else if("attrs"===p)for(var g in t[p])n.setAttribute(g,t[p][g]);else"data-"===p.substr(0,5)?n.setAttribute(p,t[p]):n[p]=t[p];else if("function"==typeof t){g=t();n.appendChild(a=u(g)?g:s.createTextNode(g)),e.push(t((function(e){u(e)&&a.parentElement?(a.parentElement.replaceChild(e,a),a=e):a.textContent=e})))}return a}for(;t.length;)i(t.shift());return n}return t.cleanup=function(){for(var t=0;t<e.length;t++)e[t]();e.length=0},t}function u(e){return e&&e.nodeName&&e.nodeType}function l(e,t){if(e.forEach)return e.forEach(t);for(var n=0;n<e.length;n++)t(e[n],n)}(e.exports=a()).context=a},function(e,t){var n,r,o;
/*!
 * Cross-Browser Split 1.1.1
 * Copyright 2007-2012 Steven Levithan <stevenlevithan.com>
 * Available under the MIT License
 * ECMAScript compliant, uniform cross-browser split method
 */
e.exports=(r=String.prototype.split,o=/()??/.exec("")[1]===n,function(e,t,i){if("[object RegExp]"!==Object.prototype.toString.call(t))return r.call(e,t,i);var s,c,a,u,l=[],d=(t.ignoreCase?"i":"")+(t.multiline?"m":"")+(t.extended?"x":"")+(t.sticky?"y":""),f=0;for(t=new RegExp(t.source,d+"g"),e+="",o||(s=new RegExp("^"+t.source+"$(?!\\s)",d)),i=i===n?-1>>>0:i>>>0;(c=t.exec(e))&&!((a=c.index+c[0].length)>f&&(l.push(e.slice(f,c.index)),!o&&c.length>1&&c[0].replace(s,(function(){for(var e=1;e<arguments.length-2;e++)arguments[e]===n&&(c[e]=n)})),c.length>1&&c.index<e.length&&Array.prototype.push.apply(l,c.slice(1)),u=c[0].length,f=a,l.length>=i));)t.lastIndex===c.index&&t.lastIndex++;return f===e.length?!u&&t.test("")||l.push(""):l.push(e.slice(f)),l.length>i?l.slice(0,i):l})},function(e,t,n){var r=n(5);function o(e){return!!e}e.exports=function(e){var t=e.classList;if(t)return t;var n={add:i,remove:s,contains:c,toggle:function(e){return c(e)?(s(e),!1):(i(e),!0)},toString:function(){return e.className},length:0,item:function(e){return a()[e]||null}};return n;function i(e){var t=a();r(t,e)>-1||(t.push(e),u(t))}function s(e){var t=a(),n=r(t,e);-1!==n&&(t.splice(n,1),u(t))}function c(e){return r(a(),e)>-1}function a(){return function(e,t){for(var n=[],r=0;r<e.length;r++)t(e[r])&&n.push(e[r]);return n}(e.className.split(" "),o)}function u(t){var r=t.length;e.className=t.join(" "),n.length=r;for(var o=0;o<t.length;o++)n[o]=t[o];delete t[r]}}},function(e,t){var n=[].indexOf;e.exports=function(e,t){if(n)return e.indexOf(t);for(var r=0;r<e.length;++r)if(e[r]===t)return r;return-1}},function(e,t){},function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});const r=n(1),o={lineWidth:18};t.rendercanvas=function(e,t,n){r.willdisplay(t,t=>{const r=e.getContext("2d");if(null===r)return!1;const i=Object.assign(Object.assign({},o),n);r.clearRect(0,0,e.width,e.height),function(e,t,n,r){const o=t/2,i=n/2,s=[[0,0,t,n],[t,0,0,n],[o,0,o,n],[0,i,t,i]];e.save();for(let o=0;o<s.length;o++){const i=s[o];e.beginPath(),e.setLineDash([t/80,n/80]),e.strokeStyle=r.grid,e.lineWidth=1,e.moveTo(i[0],i[1]),e.lineTo(i[2],i[3]),e.stroke()}e.restore()}(r,e.width,e.height,i.colorScheme),r.save(),r.lineWidth=i.lineWidth,r.lineCap="round",r.lineJoin="round";for(let e=0;e<t.length;e++){r.beginPath(),r.strokeStyle=i.colorizer(e,t.length);const n=t[e];for(let e=1;e<n.length;e++){const t=n[e-1],o=n[e];r.moveTo(t.x,t.y),r.lineTo(o.x,o.y)}r.stroke()}return r.restore(),!0})},t.renderdom=function(e,t){const n=document.getElementById(e);null!==n&&(null!==n.firstChild&&n.removeChild(n.firstChild),n.appendChild(t))}},function(e,t,n){"use strict";function r(e){return e}Object.defineProperty(t,"__esModule",{value:!0}),t._iso=()=>({unwrap:r,wrap:r})},function(e,t,n){"use strict";var r;Object.defineProperty(t,"__esModule",{value:!0}),window.db=null!=(r=window.db)?r:{};const o=window.db;function i(e){return o[e]}function s(e,t){o[e]=t}t.defaultStorage=function(){var e;return navigator.userAgent.includes("QtWebEngine")?{setItem:s,getItem:i}:null!=(e=window.localStorage)?e:window.sessionStorage},t.dump=JSON.stringify,t.parse=JSON.parse},function(e,t,n){"use strict";function r(e){return"#"+[e.r,e.g,e.b].map(e=>{const t=e.toString(16);return 1===t.length?"0"+t:t}).join("")}function o(e){let t=0,n=0,r=0;const o=e.s,i=e.v,s=e.h,c=Math.floor(6*s),a=6*s-c,u=i*(1-o),l=i*(1-a*o),d=i*(1-(1-a)*o);switch(c%6){case 0:t=i,n=d,r=u;break;case 1:t=l,n=i,r=u;break;case 2:t=u,n=i,r=d;break;case 3:t=u,n=l,r=i;break;case 4:t=d,n=u,r=i;break;case 5:t=i,n=u,r=l}return{r:Math.floor(255*t),g:Math.floor(255*n),b:Math.floor(255*r)}}function i(e,t,n=.95,i=.75){return r(o({h:e/t,s:n,v:i}))}function s(e,t,n=.95,i=.75){return r(o({h:e/.618033988749895,s:n,v:i}))}Object.defineProperty(t,"__esModule",{value:!0}),t.spectrum=i,t.contrast=s,t.none=e=>(t,n)=>e.brush,t.getColorizer=function(e,n){switch(n){case"none":return t.none(e);case"spectrum":return i;case"contrast":return s}}},function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});const r=n(0);t.canvas=e=>({height:`${r.options.frontCanvasSize}px`,width:`${r.options.frontCanvasSize}px`,border:`2px solid ${e.grid}`,background:e.gridBg}),t.result=e=>({display:"inline-block",height:`${r.options.backCanvasSize}px`,width:`${r.options.backCanvasSize}px`,border:`1px solid ${e.grid}`,background:e.gridBg}),t.wrapper=e=>({"text-align":"center"}),t.actions=e=>({}),t.action=e=>({"font-size":"22px",border:"none","border-radius":"50%",outline:"none",background:e.buttonBg,color:e.buttonIcon,display:"inline-flex",width:"44px",height:"44px",padding:"0","align-items":"center","justify-content":"center",margin:"0 5px"})},,,function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});const r=n(2),o=n(11),i=n(7),s=n(1),c=n(10),a=n(0),u=r.context(),l=a.options.backCanvasSize/a.options.frontCanvasSize,d=a.options.colorScheme(),f=u("canvas",{style:o.result(d),width:a.options.backCanvasSize*a.options.hdpiFactor,height:a.options.backCanvasSize*a.options.hdpiFactor});i.renderdom("ac-back",f);const p=s.map(s.load(),e=>({x:e.x*l,y:e.y*l}));i.rendercanvas(f,p,{lineWidth:a.options.backLineWidth*a.options.hdpiFactor,colorizer:c.getColorizer(d,d.backBrushColorizer),colorScheme:d})}]);</script>"""
      }
    ],
    css=""".card {
 font-family: arial;
 font-size: 30px;
 text-align: center;
 color: black;
 background-color: white;
}

.lookup {font-size: 12px; color:grey;}""")

DECK_IDS = {
    "Chinesisch I": 1665304798265,
    "Chinesisch II": 1683374545741,
    "Chinesisch III": 1697996748710,
    "Chinesisch IV": 1711962059715,
    "Hanzi III": 1701332896192,
    "Hanzi IV": 1711962050728
}

from data import get_db
con = get_db()

def save_audio(cur, id, text):
    cur.execute("SELECT content FROM vocab_audio WHERE id = ? AND content = ?", (id, text))
    cached = cur.fetchone()
    
    if not cached:
        speech = Speech(text, "zh-CN")
        speech.save(f"audio/{id}.mp3")
        
        cur.execute(f"INSERT INTO vocab_audio VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET content=?", (id, text, text))
        con.commit()

        time.sleep(0.3)

def save_animation(cur, id, sign):
    cur.execute("SELECT content FROM hanzi_animation WHERE id = ? AND content = ?", (id, sign))
    cached = cur.fetchone()

    if not cached:
        url = "https://www.mdbg.net/chinese/dictionary-ajax?c=cdqchi&i={}" \
            .format(urllib.parse.quote(sign))
        html = urlopen(url).read().decode('utf-8')
        p = re.compile('\'cdas\',[0-9],\'[0-9]*\'')
        num = int(p.search(html).group()[10:-1])
        url = f"https://www.mdbg.net/chinese/rsc/img/stroke_anim/{num}.gif"
        urlretrieve(url, f"hanzi/{id}.gif")

        cur.execute(f"INSERT INTO hanzi_animation VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET content=?", (id, sign, sign))
        con.commit()

        time.sleep(0.3)

def create_vocab_deck(deck_name, values):
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS vocab_audio (`id` VARCHAR(13) NOT NULL, `content` VARCHAR(255) NOT NULL, PRIMARY KEY (`id`))")

    table = values
    headers = table.pop(0)

    df = pd.DataFrame(table, columns=headers)
    my_deck = genanki.Deck(DECK_IDS[deck_name], deck_name)

    media_files = []

    for index, row in df.iterrows():
        save_audio(cur, row['Id'], row['Hanzi'])

        media_files.append(f"audio/{row['Id']}.mp3")
        my_note = genanki.Note(
            model=CHINESE_NOTE_MODEL,
            fields=[row['Deutsch'], row['Pinyin'], row['Hanzi'], f"[sound:{row['Id']}.mp3]"],
            guid=genanki.guid_for(row['Id']))

        my_deck.add_note(my_note)

    my_package = genanki.Package(my_deck)
    my_package.media_files = media_files
    my_package.write_to_file(f"{deck_name}.apkg")

    con.commit()

def create_hanzi_deck(deck_name, values):
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS hanzi_animation (`id` VARCHAR(13) NOT NULL, `content` VARCHAR(1) NOT NULL, PRIMARY KEY (`id`))")
    
    table = values
    headers = table.pop(0)

    df = pd.DataFrame(table, columns=headers) 
    my_deck = genanki.Deck(DECK_IDS[deck_name], deck_name)

    media_files = []

    for index, row in df.iterrows():
        my_note = genanki.Note(
            model=HANZI_NOTE_MODEL,
            fields=[row['Deutsch'], row['Pinyin'], row['Hanzi'], f"<img src='{row['Id']}.gif' />"],
            guid=genanki.guid_for(row['Id']))

        save_animation(cur, str(row['Id']), row['Hanzi'])
        media_files.append(f"hanzi/{row['Id']}.gif")
        my_deck.add_note(my_note)

    my_package = genanki.Package(my_deck)
    my_package.media_files = media_files
    my_package.write_to_file(f"{deck_name}.apkg")

    con.commit()


