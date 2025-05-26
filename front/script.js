window.addEventListener("DOMContentLoaded", () => {
  const textarea = document.getElementById("code");
  const stdout = document.getElementById("stdout");
  const stderr = document.getElementById("stderr");
  const variablesBox = document.getElementById("variables");

  let timeoutId = null;

  textarea.oninput = function (e) {
    clearTimeout(timeoutId);

    timeoutId = setTimeout(async () => {
      const code = e.target.value;
      try {
        const response = await axios.post("http://127.0.0.1:7677/run", { code });

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

      } catch (error) {
        stdout.innerText = "";
        stderr.innerText = "Error: " + (error.response?.data?.detail || error.message);
        variablesBox.innerText = "No variables declared";
      }
    }, 300);
  };
});
