import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";

const ICONS = {
    expand: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:1;"><path fill="none" d="m15 15l6 6M15 9l6-6m0 13v5h-5m5-13V3h-5M3 16v5h5m-5 0l6-6M3 8V3h5m1 6L3 3"/></svg>',
    close: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m3 3 10 10M13 3 3 13"/></svg>',
};

document.querySelectorAll("pre.language-mermaid").forEach((codeBlock) => {
    const container = document.createElement("div");
    container.className = "mermaid";
    container.textContent = codeBlock.textContent;
    codeBlock.replaceWith(container);
});

mermaid.initialize({ startOnLoad: false });

try {
    await mermaid.run({ querySelector: ".mermaid" });
    document.querySelectorAll(".mermaid").forEach(enhanceDiagram);
} catch (error) {
    console.error("Mermaid render failed:", error);
}

function enhanceDiagram(container) {
    const svg = container.querySelector("svg");
    if (!svg) return;

    container.classList.add("mermaid-interactive");
    container.tabIndex = 0;
    container.setAttribute("role", "button");
    container.setAttribute("aria-label", "打开 Mermaid 图表查看器");
    container.setAttribute("title", "点击放大查看");

    const expandButton = document.createElement("span");
    expandButton.className = "mermaid-expand";
    expandButton.setAttribute("aria-hidden", "true");
    expandButton.innerHTML = ICONS.expand;
    container.appendChild(expandButton);

    const open = (event) => {
        if (event.target.closest("a")) return;
        openViewer(svg);
    };
    container.addEventListener("click", open);
    container.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            openViewer(svg);
        }
    });
}

function openViewer(sourceSvg) {
    const dialog = document.createElement("div");
    dialog.className = "mermaid-viewer";
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-label", "Mermaid 图表查看器");
    dialog.innerHTML = `
        <div class="mermaid-viewer-toolbar">
            <button type="button" data-action="close" aria-label="关闭">${ICONS.close}</button>
        </div>
        <div class="mermaid-viewer-stage"></div>
    `;

    const stage = dialog.querySelector(".mermaid-viewer-stage");
    const svg = sourceSvg.cloneNode(true);
    const viewBox = svg.viewBox.baseVal;
    const naturalWidth = viewBox && viewBox.width ? viewBox.width : sourceSvg.getBoundingClientRect().width;
    const naturalHeight = viewBox && viewBox.height ? viewBox.height : sourceSvg.getBoundingClientRect().height;
    svg.removeAttribute("style");
    svg.setAttribute("width", naturalWidth);
    svg.setAttribute("height", naturalHeight);
    svg.setAttribute("aria-hidden", "true");
    stage.appendChild(svg);
    document.body.appendChild(dialog);

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    let scale = 1;
    let x = 0;
    let y = 0;
    let dragging = false;
    let pointerX = 0;
    let pointerY = 0;

    const render = () => {
        svg.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
    };
    const fit = () => {
        const padding = 64;
        scale = Math.min(
            (stage.clientWidth - padding) / naturalWidth,
            (stage.clientHeight - padding) / naturalHeight,
            1
        );
        scale = Math.max(scale, 0.05);
        x = (stage.clientWidth - naturalWidth * scale) / 2;
        y = (stage.clientHeight - naturalHeight * scale) / 2;
        render();
    };
    const zoomAt = (nextScale, clientX, clientY) => {
        nextScale = Math.min(8, Math.max(0.05, nextScale));
        const rect = stage.getBoundingClientRect();
        const pointX = clientX - rect.left;
        const pointY = clientY - rect.top;
        x = pointX - ((pointX - x) * nextScale) / scale;
        y = pointY - ((pointY - y) * nextScale) / scale;
        scale = nextScale;
        render();
    };
    const zoomCenter = (factor) => {
        const rect = stage.getBoundingClientRect();
        zoomAt(scale * factor, rect.left + rect.width / 2, rect.top + rect.height / 2);
    };
    const close = () => {
        document.removeEventListener("keydown", onKeydown, true);
        window.removeEventListener("resize", fit);
        document.body.style.overflow = previousOverflow;
        dialog.remove();
        sourceSvg.closest(".mermaid")?.focus();
    };
    const onKeydown = (event) => {
        const actions = {
            ArrowLeft: () => { x += 40; render(); },
            ArrowRight: () => { x -= 40; render(); },
            ArrowUp: () => { y += 40; render(); },
            ArrowDown: () => { y -= 40; render(); },
            Escape: close,
            "+": () => zoomCenter(1.25),
            "=": () => zoomCenter(1.25),
            "-": () => zoomCenter(0.8),
            "0": fit,
        };
        if (!actions[event.key]) return;
        event.preventDefault();
        event.stopPropagation();
        actions[event.key]();
    };

    stage.addEventListener("wheel", (event) => {
        event.preventDefault();
        zoomAt(scale * Math.exp(-event.deltaY * 0.0015), event.clientX, event.clientY);
    }, { passive: false });
    stage.addEventListener("dblclick", (event) => zoomAt(scale * 1.5, event.clientX, event.clientY));
    stage.addEventListener("pointerdown", (event) => {
        dragging = true;
        pointerX = event.clientX;
        pointerY = event.clientY;
        stage.setPointerCapture(event.pointerId);
        stage.classList.add("is-dragging");
    });
    stage.addEventListener("pointermove", (event) => {
        if (!dragging) return;
        x += event.clientX - pointerX;
        y += event.clientY - pointerY;
        pointerX = event.clientX;
        pointerY = event.clientY;
        render();
    });
    const stopDragging = () => {
        dragging = false;
        stage.classList.remove("is-dragging");
    };
    stage.addEventListener("pointerup", stopDragging);
    stage.addEventListener("pointercancel", stopDragging);

    dialog.addEventListener("click", (event) => {
        const action = event.target.closest("[data-action]")?.dataset.action;
        if (action === "close") close();
        if (event.target === dialog) close();
    });
    document.addEventListener("keydown", onKeydown, true);
    window.addEventListener("resize", fit);
    requestAnimationFrame(() => {
        fit();
        dialog.querySelector('[data-action="close"]').focus();
    });
}
