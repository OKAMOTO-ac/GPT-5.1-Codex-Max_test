const eventForm = document.getElementById("event-form");
const eventList = document.getElementById("event-list");
const refreshButton = document.getElementById("refresh");
const cancelButton = document.getElementById("cancel-edit");
const formMessage = document.getElementById("form-message");

let events = [];

const formatDate = (iso) => new Date(iso).toLocaleString("ja-JP", { hour12: false });

const showMessage = (message, type = "info") => {
  formMessage.textContent = message;
  formMessage.style.color = type === "error" ? "#ef4444" : "#6b7280";
};

const resetForm = () => {
  eventForm.reset();
  document.getElementById("event-id").value = "";
  cancelButton.hidden = true;
  showMessage("");
};

const populateForm = (event) => {
  document.getElementById("event-id").value = event.id;
  document.getElementById("title").value = event.title;
  document.getElementById("start_time").value = event.start_time.slice(0, 16);
  document.getElementById("end_time").value = event.end_time.slice(0, 16);
  document.getElementById("description").value = event.description;
  cancelButton.hidden = false;
  showMessage("編集中: 保存すると更新されます。");
  eventForm.scrollIntoView({ behavior: "smooth" });
};

const renderEvents = () => {
  if (events.length === 0) {
    eventList.innerHTML = '<div class="empty-state">まだ予定がありません。追加してみましょう。</div>';
    return;
  }

  eventList.innerHTML = events
    .map(
      (event) => `
      <article class="event-card">
        <div>
          <h3 class="event-card__title">${event.title}</h3>
          <p class="event-card__time">${formatDate(event.start_time)} 〜 ${formatDate(event.end_time)}</p>
          <p class="event-card__desc">${event.description || "(詳細なし)"}</p>
        </div>
        <div class="event-card__actions">
          <button type="button" class="ghost" data-id="${event.id}" data-action="edit">編集</button>
          <button type="button" class="danger" data-id="${event.id}" data-action="delete">削除</button>
        </div>
      </article>
    `
    )
    .join("");
};

const fetchEvents = async () => {
  const res = await fetch("/api/events");
  if (!res.ok) {
    showMessage("予定の取得に失敗しました", "error");
    return;
  }
  events = await res.json();
  renderEvents();
};

const upsertEvent = async (payload, id) => {
  const method = id ? "PUT" : "POST";
  const url = id ? `/api/events/${id}` : "/api/events";
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "保存に失敗しました");
  }

  return res.json();
};

const deleteEvent = async (id) => {
  const res = await fetch(`/api/events/${id}`, { method: "DELETE" });
  if (!res.ok) {
    throw new Error("削除に失敗しました");
  }
};

const onSubmit = async (event) => {
  event.preventDefault();
  const formData = new FormData(eventForm);
  const id = formData.get("event-id");
  const payload = {
    title: formData.get("title"),
    start_time: formData.get("start_time"),
    end_time: formData.get("end_time"),
    description: formData.get("description"),
  };

  try {
    eventForm.querySelector("button[type='submit']").disabled = true;
    const saved = await upsertEvent(payload, id);
    showMessage(id ? "予定を更新しました" : "予定を追加しました");
    resetForm();
    const existingIndex = events.findIndex((e) => e.id === saved.id);
    if (existingIndex >= 0) {
      events[existingIndex] = saved;
    } else {
      events.push(saved);
    }
    events.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    renderEvents();
  } catch (err) {
    showMessage(err.message, "error");
  } finally {
    eventForm.querySelector("button[type='submit']").disabled = false;
  }
};

const onListClick = async (event) => {
  const action = event.target.dataset.action;
  const id = event.target.dataset.id;
  if (!action || !id) return;

  const selected = events.find((e) => e.id === Number(id));
  if (!selected) return;

  if (action === "edit") {
    populateForm(selected);
    return;
  }

  if (action === "delete" && confirm("本当に削除しますか？")) {
    try {
      await deleteEvent(id);
      events = events.filter((e) => e.id !== Number(id));
      renderEvents();
      showMessage("予定を削除しました");
    } catch (err) {
      showMessage(err.message, "error");
    }
  }
};

eventForm.addEventListener("submit", onSubmit);
eventList.addEventListener("click", onListClick);
refreshButton.addEventListener("click", fetchEvents);
cancelButton.addEventListener("click", resetForm);

fetchEvents();
