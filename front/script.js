window.addEventListener("DOMContentLoaded", () => {
  const textarea = document.getElementById("code");
  const stdout = document.getElementById("stdout");
  const stderr = document.getElementById("stderr");
  const variablesBox = document.getElementById("variables");
  const inputSection = document.getElementById("input-section");
  const promptLabel = document.getElementById("prompt-label");
  const inputField = document.getElementById("input-value");
  const submitButton = document.getElementById("submit-input");

  let timeoutId = null;
  let currentCode = "";
  let inputHistory = [];

  async function runCodeWithInputs(code, inputs = []) {
    try {
      const response = await axios.post("http://127.0.0.1:7677/run", {
        code,
        inputs
      });

      const out = response.data.stdout?.trim();
      stdout.innerText = out ? out : "Output is empty";

      const err = response.data.stderr?.trim();
      stderr.innerText = err ? err : "No errors";

      const vars = response.data.variables || {};
      if (Object.keys(vars).length > 0) {
        const inline = Object.entries(vars)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([key, value]) => `${key} = ${JSON.stringify(value)}`)
          .join(", ");
        variablesBox.innerText = inline;
      } else {
        variablesBox.innerText = "No variables declared";
      }

      if (response.data.needs_input) {
        promptLabel.innerText = response.data.prompt || "Input required:";
        inputSection.style.display = "block";
        inputField.focus();
      } else {
        inputSection.style.display = "none";
        inputHistory = []; // clear when finished
      }

    } catch (error) {
      stdout.innerText = "";
      stderr.innerText = "Error: " + (error.response?.data?.detail || error.message);
      variablesBox.innerText = "No variables declared";
    }
  }

  // Handle typing in code
  textarea.oninput = function () {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      currentCode = textarea.value;
      inputHistory = []; // reset inputs when code changes
      runCodeWithInputs(currentCode, inputHistory);
    }, 300);
  };

  // Handle input submission
  submitButton.onclick = () => {
    const val = inputField.value.trim();
    if (!val) return;

    inputHistory.push(val);
    inputField.value = "";
    inputSection.style.display = "none";
    runCodeWithInputs(currentCode, inputHistory);
  };
});
