document.addEventListener("DOMContentLoaded", function () {
    const pieces = document.querySelectorAll(".piece");
    const squares = document.querySelectorAll(".chess-board td");

    pieces.forEach(piece => {
        piece.addEventListener("dragstart", dragStart);
    });

    squares.forEach(square => {
        square.addEventListener("dragover", dragOver);
        square.addEventListener("drop", drop);
    });

    function dragStart(e) {
        e.dataTransfer.setData("text/plain", e.target.id);
    }

    function dragOver(e) {
        e.preventDefault();
    }

    function drop(e) {
        e.preventDefault();

        const pieceId = e.dataTransfer.getData("text/plain");
        const piece = document.getElementById(pieceId);

        if (piece) {
            const targetSquare = e.target;
            const fromSquare = piece.parentElement.id;
            const toSquare = targetSquare.id;

            // Проверяем, является ли цель клеткой (td) и пустой ли она
            if (targetSquare.tagName === "TD" && targetSquare.children.length === 0) {
                // Отправляем ход на сервер
                fetch(`/chess/make_move/${gameId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({
                        from: fromSquare,
                        to: toSquare,
                        user: currentUser
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            console.log("Move successful!");
                            // Обновляем доску на клиентской стороне
                            targetSquare.appendChild(piece);
                        } else {
                            alert("Invalid move: " + data.error);
                        }
                    })
                    .catch(error => {
                        console.error("Error during move:", error);
                    });
            } else {
                // Если цель недействительна, вернуть фигуру на исходное место
                piece.parentElement.appendChild(piece);
            }
        }
    }
});
