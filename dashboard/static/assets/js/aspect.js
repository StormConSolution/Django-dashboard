/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (function() { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./assets/js/aspect.js":
/*!*****************************!*\
  !*** ./assets/js/aspect.js ***!
  \*****************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _aspect_aspect_modal__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./aspect/aspect-modal */ \"./assets/js/aspect/aspect-modal.js\");\n/* harmony import */ var _aspect_aspect_modal__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_aspect_aspect_modal__WEBPACK_IMPORTED_MODULE_0__);\n\n\n//# sourceURL=webpack://repustate-dashboard/./assets/js/aspect.js?");

/***/ }),

/***/ "./assets/js/aspect/aspect-modal.js":
/*!******************************************!*\
  !*** ./assets/js/aspect/aspect-modal.js ***!
  \******************************************/
/***/ (function() {

eval("let createAspectButton = document.querySelector(\n    \"#create-aspect-model\"\n);\nlet createAspectAPIKeysSelect = document.querySelector(\n    \"#create-aspect-model-api-key-select\"\n);\nlet createAspectModalLoading = document.querySelector(\n    \"#create-aspect-model-modal-loading\"\n);\nlet createAspectFirstRun = true;\ncreateAspectButton.addEventListener(\"click\", () => {\n    if (createAspectFirstRun) {\n        createAspectModalLoading.innerHTML = \"Loading...\";\n        fetch(\"/api/user-api-keys/\")\n            .then((data) => data.json())\n            .then((data) => {\n                let firstAPIKey = true\n                for (let APIKey of data[\"apikeys\"]) {\n                    let option = document.createElement(\"option\");\n                    option.innerHTML = APIKey;\n                    option.value = APIKey;\n                    if(firstAPIKey){\n                        option.selected = firstAPIKey\n                        firstAPIKey = false\n                    }\n                    createAspectAPIKeysSelect.append(option);\n                }\n                createAspectFirstRun = false;\n                createAspectModalLoading.innerHTML = \"\";\n            });\n    }\n});\n\n\n// Test sentiment modal\nlet testAspectButton = document.querySelector(\n    \"#test-aspect-button\"\n);\nlet testAspectAPIKeysSelect = document.querySelector(\n    \"#test-aspect-api-key-select\"\n);\nlet testAspectModalLoading = document.querySelector(\n    \"#test-aspect-modal-loading\"\n);\nlet testAspectFirstRun = true;\ntestAspectButton.addEventListener(\"click\", () => {\n    if (testAspectFirstRun) {\n        testAspectModalLoading.innerHTML = \"Loading...\";\n        fetch(\"/api/user-api-keys/\")\n            .then((data) => data.json())\n            .then((data) => {\n                let firstAPIKey = true\n                for (let APIKey of data[\"apikeys\"]) {\n                    let option = document.createElement(\"option\");\n                    option.innerHTML = APIKey;\n                    option.value = APIKey;\n                    if(firstAPIKey){\n                        option.selected = firstAPIKey\n                        firstAPIKey = false\n                    }\n                    testAspectAPIKeysSelect.append(option);\n                }\n                createAspectFirstRun = false;\n                testAspectModalLoading.innerHTML = \"\";\n            });\n    }\n});\n\n//# sourceURL=webpack://repustate-dashboard/./assets/js/aspect/aspect-modal.js?");

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
/******/ 	!function() {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = function(module) {
/******/ 			var getter = module && module.__esModule ?
/******/ 				function() { return module['default']; } :
/******/ 				function() { return module; };
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	!function() {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = function(exports, definition) {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	!function() {
/******/ 		__webpack_require__.o = function(obj, prop) { return Object.prototype.hasOwnProperty.call(obj, prop); }
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	!function() {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = function(exports) {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	}();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = __webpack_require__("./assets/js/aspect.js");
/******/ 	
/******/ })()
;