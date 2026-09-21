(function($) {
    $(document).ready(function() {

        function filtrarJogadores() {
            const timeA = $('#id_time_a').val();
            const timeB = $('#id_time_b').val();

            if (!timeA || !timeB) return;

            $('select[id$="-jogador"]').each(function() {
                const select = $(this);

                select.find('option').each(function() {
                    const option = $(this);

                    if (!option.val()) return;

                    const timeJogador = option.text().toLowerCase();

                    if (
                        !option.data('time-a') &&
                        !option.data('time-b')
                    ) {
                        option.hide();
                    }
                });
            });
        }

        $('#id_time_a, #id_time_b').change(function() {
            filtrarJogadores();
        });

        $(document).on('formset:added', function() {
            filtrarJogadores();
        });

    });
})(django.jQuery);
