document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.querySelector('textarea[name="topics"]');

  if (!textarea) {
    return;
  }

  const helper = document.createElement("p");
  helper.className = "empty-state";
  helper.textContent = "Tip: use one topic per line, for example: Data Structures and Algorithms | hard";
  textarea.insertAdjacentElement("afterend", helper);
  // Mark-done immediate feedback: change button to check + disable on click
  const markButtons = document.querySelectorAll('.mark-done-btn');
  markButtons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      try {
        btn.disabled = true;
        btn.classList.add('done');
        btn.innerText = '✓ Done';
      } catch (err) {
        // ignore
      }
      // allow the form to submit normally
    });
  });
});