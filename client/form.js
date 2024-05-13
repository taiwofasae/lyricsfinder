var lyrics = [
    {title: 'gospel',content: ''},
    {title: 'dance',content: ''},
    {title: 'classical',content: ''},
    {title: 'example',content: ''}
];

search_result = {
    uuid: '',
    lyrics: [],
    status: true
}

ids = {
    search_phrase: '#search_phrase',
    lyrics_list: 'ul#lyrics_list',
    lyric_title: '#title',
    lyric_content: '#content',
    uuid: '#uuid',
    sim_score: '#sim_score',
    content_pane: '#page_con'
};

classes = {
    search_phrase: '.search_phrase'
}

post_url = window.LYRICSAPP_POST_URL

lyrics_list = {
    get_template: function () {
        return $(ids.lyrics_list + ' li:first').clone()
    },
    
    reset: function () {
        $(ids.lyrics_list + ' li').html('').addClass('hidden').removeClass('active');
    },
    
    set_data: function (data, index){
        title = `${index + 1}. ${data.title} (${data.sim_score})`;
        $($(ids.lyrics_list + ' li')[index]).html(title).removeClass('hidden');
    },
    
    highlight: function (index){
        $(ids.lyrics_list + ' li').removeClass('active');
        $($(ids.lyrics_list + ' li')[index]).addClass('active')
    },

    select: function (index){
        lyrics_board.clear()
        this.highlight(index);
        lyrics_board.set(lyrics[index])
    },
    
    populate: function (lyrics) {
        lyrics = lyrics == null ? [] : lyrics
    
        this.reset();
        
        lyrics.forEach((e, i) => {
            this.set_data(e, i);
        });
    
        return true
    }
}

lyrics_board = {
    clear: () => {
        $(ids.lyric_title).html('?')
        $(ids.lyric_content).html('?')
    },
    set: (data) => {
        $(ids.lyric_title).text(data.title)
        $(ids.lyric_content).val(data.lyrics)
        $(ids.sim_score).text(data.sim_score)
        $(classes.search_phrase).text($(ids.search_phrase).val())
    },

    show_pane: () => $(ids.content_pane).removeClass('hidden')
}

const generate_custom_uuid = () => ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16)
    )

    

search_box = {
    reset: () => {
        uuid = generate_custom_uuid().substring(0,36)
        $(ids.uuid).val(uuid)
    },
    clear: () => {
        this.reset()
        $(ids.search_phrase).val('')
    }
}



animations = {
    done: () => {
        $("#done").removeClass("hidden")

        setTimeout(() => {$("#done").addClass("hidden")}, 5000)
    },
    loading: {
        start: x => $("#loader").removeClass("hidden"),
        end: x => $("#loader").addClass("hidden")
    }
}

mock_api = function(){
    return new Promise((resolve) => {
        setTimeout(()=>{
            resolve(lyrics);
        }, 5000);
    });
}

window.poller = 0
window.poller_count = 0
window.POLLER_STARTED = false

polling = {
    start: function(){
        if (window.POLLER_STARTED) return

        window.poller = setInterval(_ => {
            if (window.poller_count < 10) $("form").submit()
            else {
                console.log("Polled api 10 times. Forcing it now...")
                clearInterval(window.poller)
            }
            window.poller_count++
        }, 2000)
        window.POLLER_STARTED = true
    },
    stop: function(){
        clearInterval(window.poller)
        window.POLLER_STARTED = false
    }
}

$(document).ready(function () {

    $(ids.lyrics_list + ' li').on("click", function(){
        var index = $(ids.lyrics_list + ' li').index(this);
        lyrics_list.select(index);
    })

    search_box.reset()


    $("form").submit(function (event) {

        animations.loading.start()
        lyrics_list.reset()
        
      var formData = {
        uuid: $(ids.uuid).val(),
        search_phrase: $(ids.search_phrase).val(),
      };
  
      $.ajax({
        type: "POST",
        url: post_url,
        data: formData,
        dataType: "json",
        encode: true,
      }).done(function (data) {
        if (data.status){
            lyrics_list.populate(data.lyrics)
            lyrics = data.lyrics
            lyrics_list.select(0);
            animations.done();
            animations.loading.end()

            search_box.reset()

            lyrics_board.show_pane()

            polling.stop()
        }
        else polling.start()

      }).error(e => {
        console.log(e)
        animations.loading.end()
        polling.stop()
    }).complete(() => {
        
      });


        // mock_api().then(()=>{
        //     lyrics_list.populate(lyrics);
        //     lyrics_list.select(0);
        //     animations.done();
        //     animations.loading.end()
        // },
        // () => { 
        //     animations.loading.end()
        // });
   
    
        event.preventDefault();
    });
  });