const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const resultPic = document.getElementById("result-pic");
const resultName = document.getElementById("result-name");

const MAX_SIZE = 8_000_000;

function setStatus(msg) {
  statusEl.textContent = msg || "";
}

function showResult(data) {
  resultPic.src = data.pic || "";
  resultPic.alt = data.common_name || data.species || "";
  resultName.textContent = data.common_name ? `${data.common_name} (${data.species})` : data.species;
  resultEl.hidden = false;
}

async function uploadFile(file) {
  if (!file.type.startsWith("image/")) {
    setStatus("Please drop an image file.");
    return;
  }
  if (file.size > MAX_SIZE) {
    setStatus("Image too large (max 8MB).");
    return;
  }
  setStatus("Identifying...");

  const reader = new FileReader();
  reader.onload = async () => {
    const dataUrl = reader.result;
    const b64 = dataUrl.replace(/^data:[^,]+,/, "");
    try {
      const res = await fetch("/bioclip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({ image_b64: b64 })
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        setStatus(`Error: ${detail.detail || res.statusText}`);
        return;
      }
      const data = await res.json();
      setStatus("");
      showResult(data);
    } catch (err) {
      setStatus(`Network error: ${err.message}`);
    }
  };
  reader.readAsDataURL(file);
}

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files && e.dataTransfer.files[0];
  if (file) uploadFile(file);
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files && fileInput.files[0];
  if (file) uploadFile(file);
});
