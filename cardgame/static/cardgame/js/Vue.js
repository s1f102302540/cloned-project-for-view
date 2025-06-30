function joinSession(sessionId) {
    $.ajax({
        url: "{% url 'cardgame:join_session' session_id=0 %}".replace("0", sessionId),
        method: "POST",
        headers: { "X-CSRFToken": "{{ csrf_token }}" },
        success: function (data) {
            if (data.success) {
                window.location.href = `/session/${data.session_id}/dashboard/`;
            } else {
                alert(data.message);
            }
        },
        error: function () {
            alert("Failed to join session.");
        },
    });
}