document.addEventListener("DOMContentLoaded", function() {
  const input = document.getElementById("customInput");

input.addEventListener("input", function () {
    const cursorPosition = this.selectionStart; // 保存当前光标位置

    if (this.value && this.value.slice(-1) !== "?") {
        this.value = this.value.replace("?", ""); // 移除已经存在的 "?"
        this.value += "?"; // 在字符串末尾添加一个 "?"

        // 设置光标位置
        this.selectionStart = cursorPosition;
        this.selectionEnd = cursorPosition;
    } else if (!this.value.slice(0, -1)) {
        // 如果输入框的值为空，移除 "?"
        this.value = this.value.replace("?", "");
    }

    // 首字母大写逻辑
    const value = this.value;
    if (value.length === 1) {
        this.value = value.toUpperCase();
    } else if (value.length > 1) {
        this.value = value.charAt(0).toUpperCase() + value.slice(1, -1) + value.slice(-1);
    }
});

  // 当输入框失去焦点时，确保 "?" 在光标前
  input.addEventListener("blur", function() {
    if (this.value.slice(-1) === "?") {
      this.value = this.value.slice(0, -1);
    }
  });

  // 当输入框获得焦点时，添加 "?"（如果需要）
  input.addEventListener("focus", function() {
    if (this.value && this.value.slice(-1) !== "?") {
      this.value += "?";
    }
  });
});

document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('customInput');
    const confirmButton = document.getElementById('question_create_confirm');

    input.addEventListener('input', function () {
        if (input.value.trim().length > 0) {
            confirmButton.removeAttribute('disabled');
        } else {
            confirmButton.setAttribute('disabled', '');
        }
    });
});