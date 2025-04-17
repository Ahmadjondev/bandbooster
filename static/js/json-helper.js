/**
 * JSON Helper Functions for IELTS Mock Test Platform
 *
 * This file contains utility functions for handling JSON data
 * in the IELTS Mock Test platform.
 */

// Parse JSON safely with error handling
function safeJSONParse(jsonString) {
    if (!jsonString) return null

    try {
        if (typeof jsonString === "object") return jsonString
        return JSON.parse(jsonString)
    } catch (error) {
        console.error("Error parsing JSON:", error)
        console.log("Problematic JSON string:", jsonString)
        return null
    }
}

// Get a nested property from an object safely
function getNestedProperty(obj, path, defaultValue = null) {
    if (!obj) return defaultValue

    const keys = path.split(".")
    let current = obj

    for (const key of keys) {
        if (current === null || current === undefined || typeof current !== "object") {
            return defaultValue
        }
        current = current[key]
    }

    return current !== undefined ? current : defaultValue
}

// Convert Django QueryDict to JavaScript object
function queryDictToObject(queryDict) {
    if (!queryDict || typeof queryDict !== "object") return {}

    const result = {}

    for (const key in queryDict) {
        if (Object.prototype.hasOwnProperty.call(queryDict, key)) {
            result[key] = queryDict[key]
        }
    }

    return result
}

// Debug function to display JSON structure
function debugJSONStructure(jsonObj, elementId) {
    if (!jsonObj) return

    const element = document.getElementById(elementId)
    if (!element) return

    let structureText = ""

    function processObject(obj, indent = 0) {
        const indentStr = " ".repeat(indent)

        if (Array.isArray(obj)) {
            structureText += `${indentStr}Array(${obj.length}):\n`
            obj.forEach((item, index) => {
                if (index < 3 || index === obj.length - 1) {
                    structureText += `${indentStr}  [${index}]: `
                    if (typeof item === "object" && item !== null) {
                        structureText += "\n"
                        processObject(item, indent + 4)
                    } else {
                        structureText += `${typeof item}\n`
                    }
                } else if (index === 3) {
                    structureText += `${indentStr}  ... ${obj.length - 4} more items ...\n`
                }
            })
        } else if (typeof obj === "object" && obj !== null) {
            const keys = Object.keys(obj)
            structureText += `${indentStr}Object(${keys.length} keys):\n`
            keys.forEach((key) => {
                structureText += `${indentStr}  "${key}": `
                if (typeof obj[key] === "object" && obj[key] !== null) {
                    structureText += "\n"
                    processObject(obj[key], indent + 4)
                } else {
                    structureText += `${typeof obj[key]}\n`
                }
            })
        }
    }

    processObject(jsonObj)
    element.textContent = structureText
}

// Export functions for use in other files
window.JSONHelper = {
    safeJSONParse,
    getNestedProperty,
    queryDictToObject,
    debugJSONStructure,
}
