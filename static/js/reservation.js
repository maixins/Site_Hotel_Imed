$(document).ready(function() {
    $('#search_nom, #search_prenom').on('input', function() {
        let nom = $('#search_nom').val();
        let prenom = $('#search_prenom').val();

        $.ajax({
            url: '/search_client',
            method: 'GET',
            data: {
                nom: nom,
                prenom: prenom
            },
            success: function(clients) {
                $('#client-results').empty();
                if (clients.length > 0) {
                    clients.forEach(client => {
                        $('#client-results').append(`<div class="client-item">${client.nom} ${client.prenom}</div>`);
                    });
                } else {
                    $('#client-results').append('<div class="client-item">Aucun client trouvé</div>');
                }
            }
        });
    });

    $('#lit_simple, #lit_double, #salle_bain').on('input change', function() {
        let lit_simple = $('#lit_simple').val();
        let lit_double = $('#lit_double').val();
        let salle_bain = $('#salle_bain').is(':checked') ? '1' : '0';

        $.ajax({
            url: '/search_room',
            method: 'GET',
            data: {
                lit_simple: lit_simple,
                lit_double: lit_double,
                salle_bain: salle_bain
            },
            success: function(rooms) {
                $('#room-results').empty();
                if (rooms.length > 0) {
                    rooms.forEach(room => {
                        $('#room-results').append(`<div class="room-item">Chambre ${room.id} - ${room.description}</div>`);
                    });
                } else {
                    $('#room-results').append('<div class="room-item">Aucune chambre trouvée</div>');
                }
            }
        });
    });
});
