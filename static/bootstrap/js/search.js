$(document).ready(function() {
    $('#button-search').click(function() {
      var searchQuery = $('input').val();
      $.ajax({
        url: '/search',
        type: 'POST',
        data: { 'search_query': searchQuery },
        success: function(response) {
          $('tbody').html(response);
        }
      });
    });
  });
  