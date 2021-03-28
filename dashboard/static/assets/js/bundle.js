/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./assets/js/dashboard/config.js":
/*!***************************************!*\
  !*** ./assets/js/dashboard/config.js ***!
  \***************************************/
/***/ ((module) => {

eval("module.exports = {\n    primary : \"#5A8DEE\",\n    success : \"#39DA8A\",\n    danger : \"#FF5B5C\",\n    warning : \"#FDAC41\",\n    info : \"#00CFDD\",\n    label_color : \"#FFFFFF\",\n    primary_light : \"#E2ECFF\",\n    danger_light : \"#ffeed9\",\n    gray_light : \"#828D99\",\n    label_trend : \"#f5eff7\",\n    sub_label_color : \"#596778\",\n    radial_bg : \"#e7edf3\",\n    positive : \"#28C76F\",\n    negative : \"#EA5455\",\n    neutral: \"#00CFE8\"\n}\n\n//# sourceURL=webpack://repustate-dashboard/./assets/js/dashboard/config.js?");

/***/ }),

/***/ "./assets/js/dashboard/graphs.js":
/*!***************************************!*\
  !*** ./assets/js/dashboard/graphs.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _graphs_overall_sentiment__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./graphs/overall-sentiment */ \"./assets/js/dashboard/graphs/overall-sentiment.js\");\n/* harmony import */ var _graphs_volume_by_source__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./graphs/volume-by-source */ \"./assets/js/dashboard/graphs/volume-by-source.js\");\n/* harmony import */ var _graphs_aspect_count__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./graphs/aspect-count */ \"./assets/js/dashboard/graphs/aspect-count.js\");\n/* harmony import */ var _graphs_co_occurrence__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./graphs/co-occurrence */ \"./assets/js/dashboard/graphs/co-occurrence.js\");\n/* harmony import */ var _graphs_aspect_by_sentiment__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./graphs/aspect-by-sentiment */ \"./assets/js/dashboard/graphs/aspect-by-sentiment.js\");\n//import \"./graphs/sentiment-per-entity\";\n//import \"./graphs/top-topics-per-aspect\";\n//import \"./graphs/sentiment-per-aspect\";\n\n\n\n\n\n\n//# sourceURL=webpack://repustate-dashboard/./assets/js/dashboard/graphs.js?");

/***/ }),

/***/ "./assets/js/dashboard/graphs/aspect-by-sentiment.js":
/*!***********************************************************!*\
  !*** ./assets/js/dashboard/graphs/aspect-by-sentiment.js ***!
  \***********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../config */ \"./assets/js/dashboard/config.js\");\n/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_config__WEBPACK_IMPORTED_MODULE_0__);\n\nvar chartOptions = {\n    series: [],\n    chart: {\n        type: \"bar\",\n        height: 440,\n        stacked: true,\n    },\n    legend: { show: false },\n    colors: [\"#28C76F\", \"#EA5455\"],\n    plotOptions: {\n        bar: {\n            horizontal: true,\n            borderRadius: 6,\n            barHeight: \"50\",\n        },\n    },\n    dataLabels: {\n        enabled: false,\n    },\n    stroke: {\n        width: 1,\n        colors: [\"#fff\"],\n    },\n\n    grid: {\n        xaxis: {\n            lines: {\n                show: false,\n            },\n        },\n    },\n    yaxis: {\n        min: -85,\n        max: 85,\n        title: {\n            // text: 'Age',\n        },\n    },\n    tooltip: {\n        shared: false,\n        x: {\n            formatter: function (val) {\n                return val;\n            },\n        },\n        y: {\n            formatter: function (val) {\n                return Math.abs(val);\n            },\n        },\n    },\n\n    xaxis: {\n        categories: [],\n\n        labels: {\n            formatter: function (val) {\n                return Math.abs(Math.round(val));\n            },\n        },\n    },\n};\n\nfetch(`/api/sentiment-per-aspect/${window.project_id}/`).then(response => response.json()).then(data => {\n    let positiveData = []\n    let negativeData = []\n    let aspects = []\n    let maxPositive = 0;\n    let maxNegative = 0;\n    for(let element of data){\n        positiveData.push(element.positiveCount)\n        negativeData.push(-element.negativeCount)\n        aspects.push(element.aspectLabel)\n        if(element.positiveCount > maxPositive){\n            maxPositive = element.positiveCount\n        }\n        if(element.negativeCount > maxNegative){\n            maxNegative = element.negativeCount\n        }\n    }\n    chartOptions.series.push({\n        name: 'Positives',\n        data: positiveData\n    })\n    chartOptions.series.push({\n        name: 'Negatives',\n        data: negativeData\n    })\n    chartOptions.yaxis.max = maxPositive + Math.round(maxPositive * 0.1);\n    chartOptions.yaxis.min = -maxNegative - Math.round(maxNegative * 0.1);\n    chartOptions.xaxis.categories = aspects\n    var chart = new ApexCharts(document.querySelector(\"#aspect-by-sentiment\"), chartOptions);\n    chart.render();\n})\n\n\n//# sourceURL=webpack://repustate-dashboard/./assets/js/dashboard/graphs/aspect-by-sentiment.js?");

/***/ }),

/***/ "./assets/js/dashboard/graphs/aspect-count.js":
/*!****************************************************!*\
  !*** ./assets/js/dashboard/graphs/aspect-count.js ***!
  \****************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../config */ \"./assets/js/dashboard/config.js\");\n/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_config__WEBPACK_IMPORTED_MODULE_0__);\n\nlet colors = [\"#28C76F\", \"#EA5455\", \"#00CFE8\", \"#7367F0\", \"#FF9F43\"];\nlet colorsIndex = 0;\n\nlet aspectCountGraphs = document.querySelector(\"#aspect-count-graphs\");\n\nlet project_id = window.project_id;\nfetch(`/api/aspect-count/${project_id}/`)\n    .then((response) => response.json())\n    .then((data) => {\n        let totalCount = 0\n        for(let element of data){\n            totalCount += element.aspectCount\n        }\n        for (let element of data) {\n            let percentage = (element.aspectCount/totalCount * 100).toFixed(2)\n            let id = `aspect-count-${element.aspectLabel}`\n            let li = document.createElement(\"li\")\n\n            let domElement = `\n            <a href=\"#\" class=\"d-flex color-1\">\n            <small>${element.aspectLabel}</small>\n            <b style=\"color:${colors[colorsIndex]};\">${element.aspectCount}</b>\n            <span>${percentage}%</span>\n            <div class=\"round-chart\">\n              <div id=\"${id}\"></div>\n            </div>\n            </a>\n            `;\n            li.innerHTML = domElement;\n            aspectCountGraphs.append(li)\n            let color = colors[colorsIndex];\n            if(colorsIndex == colors.length - 1){\n                colorsIndex = 0\n            } else {\n                colorsIndex++\n            }\n\n            let chartOptions = {\n                series: [percentage],\n                chart: {\n                    type: \"radialBar\",\n                    width: 30,\n                    height: 30,\n                    sparkline: {\n                        enabled: true,\n                    },\n                },\n\n                colors: [color],\n                dataLabels: {\n                    enabled: false,\n                },\n                plotOptions: {\n                    radialBar: {\n                        hollow: {\n                            margin: 0,\n                            size: \"40%\",\n                        },\n                        track: {\n                            margin: 0,\n                        },\n                        dataLabels: {\n                            show: false,\n                        },\n                    },\n                },\n            };\n            let chart = new ApexCharts(\n                document.querySelector(`#${id}`),\n                chartOptions\n            );\n            chart.render();\n        }\n    });\n\n\n//# sourceURL=webpack://repustate-dashboard/./assets/js/dashboard/graphs/aspect-count.js?");

/***/ }),

/***/ "./assets/js/dashboard/graphs/co-occurrence.js":
/*!*****************************************************!*\
  !*** ./assets/js/dashboard/graphs/co-occurrence.js ***!
  \*****************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../config */ \"./assets/js/dashboard/config.js\");\n/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_config__WEBPACK_IMPORTED_MODULE_0__);\n\nvar chartOptions = {\n    series: [],\n    chart: {\n        height: 480,\n        type: \"heatmap\",\n    },\n    plotOptions: {\n        heatmap: {\n            shadeIntensity: 0.5,\n            radius: 0,\n\n            colorScale: {\n                ranges: [\n                    {\n                        from: 0,\n                        to: 20,\n                        name: \"0-20\",\n                        color: \"#E2E0FB\",\n                    },\n                    {\n                        from: 21,\n                        to: 40,\n                        name: \"21-40\",\n                        color: \"#D4D0FA\",\n                    },\n                    {\n                        from: 41,\n                        to: 60,\n                        name: \"41-60 \",\n                        color: \"#C6C1F8\",\n                    },\n                    {\n                        from: 61,\n                        to: 80,\n                        name: \"61-80\",\n                        color: \"#968DF3\",\n                    },\n                    {\n                        from: 81,\n                        to: 99,\n                        name: \"81-99\",\n                        color: \"#8075F1\",\n                    },\n                    {\n                        from: 100,\n                        to: 100,\n                        name: \"100\",\n                        color: \"#7367F0\",\n                    },\n                ],\n            },\n        },\n    },\n    dataLabels: {\n        enabled: false,\n        style: {\n            fontSize: \"14px\",\n            fontFamily: \"Helvetica, Arial, sans-serif\",\n            fontWeight: \"bold\",\n        },\n    },\n    legend: {\n        position: \"bottom\",\n\n        markers: {\n            width: 30,\n        },\n    },\n\n    stroke: {\n        width: 1,\n    },\n    xaxis: {\n        type: \"category\",\n        categories: [],\n    },\n};\nlet project_id = window.project_id;\nfetch(`/api/co-occurence/${project_id}/`)\n    .then((response) => response.json())\n    .then((data) => {\n        chartOptions.series = data\n        let chart = new ApexCharts(\n            document.querySelector(\"#co-occurrence-graph\"),\n            chartOptions\n        );\n        chart.render();\n    });\n\n\n//# sourceURL=webpack://repustate-dashboard/./assets/js/dashboard/graphs/co-occurrence.js?");

/***/ }),

/***/ "./assets/js/dashboard/graphs/overall-sentiment.js":
/*!*********************************************************!*\
  !*** ./assets/js/dashboard/graphs/overall-sentiment.js ***!
  \*********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../config */ \"./assets/js/dashboard/config.js\");\n/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_config__WEBPACK_IMPORTED_MODULE_0__);\n\nvar chartOptions = {\n    colors: [(_config__WEBPACK_IMPORTED_MODULE_0___default().positive), (_config__WEBPACK_IMPORTED_MODULE_0___default().negative), (_config__WEBPACK_IMPORTED_MODULE_0___default().neutral)],\n    chart: {\n        height: 250,\n        type: \"donut\",\n    },\n    dataLabels: {\n        enabled: false,\n    },\n    legend: {\n        position: \"left\",\n    },\n    plotOptions: {\n        pie: {\n            donut: {\n                labels: {\n                    show: true,\n                    total: {\n                        showAlways: true,\n                        show: true,\n                    },\n                },\n            },\n        },\n        radialBar: {\n            hollow: {\n                size: \"60%\",\n            },\n        },\n    },\n    labels: [\"Positive\", \"Negative\", \"Neutral\"],\n};\nlet project_id = window.project_id\nfetch(`/api/sentiment-count/${project_id}/`).then(response => response.json()).then(data => {\n    chartOptions.series = [data.positive_count, data.negative_count, data.neutral_count]\n    let chart = new ApexCharts(document.querySelector(\"#overall-sentiment-chart\"), chartOptions);\n    chart.render();\n})\n\n\n\n//# sourceURL=webpack://repustate-dashboard/./assets/js/dashboard/graphs/overall-sentiment.js?");

/***/ }),

/***/ "./assets/js/dashboard/graphs/volume-by-source.js":
/*!********************************************************!*\
  !*** ./assets/js/dashboard/graphs/volume-by-source.js ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../config */ \"./assets/js/dashboard/config.js\");\n/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_config__WEBPACK_IMPORTED_MODULE_0__);\n\nvar chartOptions = {\n    series: [],\n    colors: [(_config__WEBPACK_IMPORTED_MODULE_0___default().neutral)],\n    chart: {\n        type: \"bar\",\n        height: 320,\n    },\n    plotOptions: {\n        bar: {\n            borderRadius: 6,\n            horizontal: true,\n            barHeight: \"24\",\n        },\n    },\n    dataLabels: {\n        enabled: false,\n    },\n    xaxis: {\n        categories: []\n    }\n};\nlet project_id = window.project_id;\nfetch(`/api/volume-by-source/${project_id}/`)\n    .then((response) => response.json())\n    .then((data) => {\n        let series = []\n        let categories = []\n        for(let element of data){\n            series.push(element.sourceCount)\n            categories.push(element.sourceName)\n        }\n        chartOptions.series.push({\n            data: series\n        })\n        chartOptions.xaxis.categories = categories\n        let chart = new ApexCharts(\n            document.querySelector(\"#volume-by-source\"),\n            chartOptions\n        );\n        chart.render();\n    });\n\n\n//# sourceURL=webpack://repustate-dashboard/./assets/js/dashboard/graphs/volume-by-source.js?");

/***/ }),

/***/ "./assets/js/project-graphs.js":
/*!*************************************!*\
  !*** ./assets/js/project-graphs.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _dashboard_graphs__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./dashboard/graphs */ \"./assets/js/dashboard/graphs.js\");\n\n\n//# sourceURL=webpack://repustate-dashboard/./assets/js/project-graphs.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = __webpack_require__("./assets/js/project-graphs.js");
/******/ 	
/******/ })()
;