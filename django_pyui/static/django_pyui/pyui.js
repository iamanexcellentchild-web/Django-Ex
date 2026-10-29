document.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) {
    return;
  }

  const trigger = event.target.closest("[data-pyui-toggle]");
  if (!trigger) {
    return;
  }

  const selector = trigger.getAttribute("data-pyui-toggle");
  const target = document.querySelector(selector);
  if (!target) {
    throw new Error(`PyUI toggle target not found: ${selector}`);
  }

  target.hidden = !target.hidden;
  trigger.setAttribute("aria-expanded", String(!target.hidden));
});
