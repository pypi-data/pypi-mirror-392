const fixOption = (operationSelect, contentInput) => {
        if (operationSelect.value === "bool") {
            contentInput.style.display = "none"
            contentInput.required = false
        } else {
            contentInput.style.display = "block"
            contentInput.required = true
        }
}
const addOptionFixer = (element) => {
    const operationSelect = element.querySelector("select[id$='condition_operation']")
    const contentInput = element.querySelector(".rule-content")  // can be select or input or datepicker etc
    operationSelect.addEventListener("change", () => {
        fixOption(operationSelect, contentInput)
    })
    fixOption(operationSelect, contentInput)
}

const addAllOptionFixers = () => {
    document.querySelectorAll(".question-option-row").forEach(element => addOptionFixer(element))
}

document.querySelector("#add-formset").addEventListener("click", () => {
    window.setTimeout(addAllOptionFixers, 1000)
})

addAllOptionFixers()
