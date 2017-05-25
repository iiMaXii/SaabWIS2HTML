
var tab_icons = {
  '0902': '<i class="fa fa-tachometer fa-2x" aria-hidden="true"></i>', // Teknisk data
  '1101': '<i class="fa fa-wrench fa-2x" aria-hidden="true"></i>', // Specialverktyg
  '0301': '<i class="fa fa-cogs fa-2x" aria-hidden="true"></i>', // Teknisk beskrivning
  '0601': '<i class="fa fa-medkit fa-2x" aria-hidden="true"></i>', // Felsökning, allmänt
  '0602': '<i class="fa fa-terminal fa-2x" aria-hidden="true"></i>', // Felsökning, felkoder
  '0603': '<i class="fa fa-thermometer-empty fa-2x" aria-hidden="true"></i>', // Felsökning, symptom
  '0801': '<i class="fa fa-exchange fa-2x" aria-hidden="true"></i>', // Justering, byte
  '0401': '<i class="fa fa-arrows fa-2x" aria-hidden="true"></i>', // Komponentplacering
  '1001': '<i class="fa fa-microchip fa-2x" aria-hidden="true"></i>', // Elschema
  '0500': '<i class="fa fa-info fa-2x" aria-hidden="true"></i>', // Bulletiner - SI/MI (Teknisk data)
  '0701': '<i class="fa fa-car fa-2x" aria-hidden="true"></i>', // Service
};

var active_item = undefined;
var active_tab = undefined;
var active_tab_item = undefined;

var submenus = {};
var references = {};


/*function get_active_tab_id() {
  var current_tab = $('.nav-item.active');
  
  if (current_tab.length) {
    return current_tab.attr('id').substring(4);
  }
}*/

function history_snapshot() {
  var scroll_top = $('html,body').scrollTop();
  console.log('History snapshot: {item='+active_item+', tab='+active_tab+', sub_item='+active_tab_item+', scroll_top='+scroll_top+'}');
  
  var active_menu_item = $('#treeview1').treeview('getSelected')[0];
  
  history.pushState({'item': active_item, 'item_node_id': active_menu_item.nodeId, 'tab': active_tab, 'sub_item': active_tab_item, 'scroll_top': scroll_top}, "Page title wop wop", "/");
}

window.addEventListener('popstate', function (event) {
  var data = event.state;
  if (!data) {
    alert('Error: empty history state');
  }
  
  console.log('popstate event');
  console.log(data);
  
  if (data['item'] !== active_item) {
    //open_menu(data['item']);
    console.log('wop');
    $('#treeview1').treeview('selectNode', data['item_node_id'], { silent: true });
    //open_menu(data['item']);
  }
  
  if (data['tab'] !== active_tab) {
    open_tab(data['tab']);
  }
  
  if (data['tab_item'] !== active_tab_item) {
    open_doc(data['tab_item']);
  }
});

function resolve_reference(id) {
  if (references.length == 0) {
    alert('References has not been loaded yet');
    return;
  }

  console.log(references)
  console.log(references[id])
  return references[id];
}

$(document).ready(function() {
  //history_snapshot();
  
  console.log('Loading tabs.json');
  $.getJSON("/static/data/se/index/tabs.json", function(data) {
    console.log('Got tabs.json');
    $.each(data, function (index, data) {
      
      var value;
      if (data.id in tab_icons) {
        value = tab_icons[data.id];
      } else {
        value = data.name;
      }
      
      $('#tab-menu').append('<li title="'+data.name+'" id="tab-'+data.id+'" class="nav-item disabled"><a class="nav-link" data-toggle="tab" href="#tab-pane-'+data.id+'" role="tab">'+value+'</a></li>');
      $('#tab-content').append('<div class="tab-pane" id="tab-pane-'+data.id+'" role="tabpanel"><div id="tab-content-'+data.id+'" role="tab-content"></div><div id="tab-tree-'+data.id+'" role="tab-submenu-tree"></div></div>');
    });
    $('#tab-menu a').on('shown.bs.tab', function (e) {
      var id = $(e.target).parent().attr('id').substring(4);
      active_tab = id;
    });
  });

  console.log('Loading menu.json');
  $.getJSON("/static/data/se/index/menu.json", function(data) {
    $('#treeview1').treeview({
      data: data,
      onNodeSelected: function(event, data) {
        var submenu_identifier = data['data-id'];
        open_menu(submenu_identifier);
        
        history_snapshot();
      }
    });
  });

  console.log('Loading submenus.json');
  $.getJSON("/static/data/se/index/submenus.json", function(data) {
    console.log('Got submenus.json');
    submenus = data;
  });

  console.log('Loading references.json');
  $.getJSON("/static/data/se/index/references.json", function(data) {
    console.log('Got references.json');
    references = data;
  });

  $('#img01').click(function() {
    window.location = this.src;
  });
});

function open_tab(tab_id) {
  var current_tab = $('.nav-item.active');
  if (current_tab.length && current_tab.attr('id').substring(4) === tab_id) {
    console.log('Tab already active')
    return;
  }
  
  $('.nav-tabs a[href="#tab-pane-' + tab_id + '"]').tab('show');
}

function open_menu(submenu_identifier) {
  if (active_item === submenu_identifier) {
    console.log('Menu is already open');
    // TODO scroll down?
    return;
  }
  
  if (submenu_identifier === undefined) {
    $('#treeview1').treeview('selectNode', 10, {silent: false});
  }
  
  active_item = submenu_identifier;

  console.log('Loading submenu '+submenu_identifier);
  if (jQuery.isEmptyObject(submenus)) {
    alert('Still loading, please wait');
    return;
  }

  $('#tab-menu li').addClass('disabled');

  // Clear content of all tabs
  $('div[role=tab-content]').empty();
  //$('div[role=tab-submenu-tree]').treeview('remove');
  $('.treeview[role=tab-submenu-tree]').each(function(index) {
    if ($(this).hasClass('treeview')) {
      $(this).treeview('remove');
    }
  });
  //$('div[role=tabpanel]').removeClass('active');

  //history_snapshot();

  $.each(submenus[submenu_identifier], function(id, value) {
    //active_tab = id;
    $('#tab-tree-'+id).treeview({
      data: value,
      onNodeSelected: function(event, data) {
        //history_snapshot();
        open_doc(data['data-id']);
        /*console.log("/static/data/se/doc"+data['data-id']+".html");
        $('#tab-content-'+id).load("/static/data/se/doc"+data['data-id']+".html", function() {
          var modal = document.getElementById('myModal');
          var modalImg = document.getElementById("img01");
          $('#tab-content-'+id+' img').click(function() {
            //var captionText = document.getElementById("caption");
            modal.style.display = "block";
            modalImg.src = this.src;
            $("#myModal").modal();
          }).css('cursor', 'pointer');
        });*/
      }
    });

    //console.log('page_history.add('+active_item+', '+active_tab+', '+active_tab_item+')');
    //page_history.add(active_item, active_tab, active_tab_item);

    console.log('Activating tab id='+id);
    $('#tab-'+id).removeClass('disabled');

  });
}

function open_doc(document_identifier, anchor) {
  if (active_tab === undefined) {
    alert('Error: No tab active');
    return;
  }
  
  active_tab_item = document_identifier;

  console.log('Loading doc'+document_identifier+' into tab'+active_tab)
  $('#tab-content-'+active_tab).load("/static/data/se/doc"+document_identifier+".html", function() {
    if (typeof(anchor)==='undefined') {
      $('html,body').scrollTop(0);
    } else {
      location.href = anchor;
    }

    var modal = document.getElementById('myModal');
    var modalImg = document.getElementById("img01");

    $('#tab-content-'+active_tab+' img').click(function() {
      modal.style.display = "block";
      modalImg.src = this.src;
      $("#myModal").modal();

    }).css('cursor', 'pointer');

    $(".doc-ref").click(function(event) {
      event.preventDefault();
      link_id = this.getAttribute('href').substring(1);
      console.log(link_id);
      ref = resolve_reference(link_id);

      console.log(ref);
      
      //history_snapshot();
      
      open_menu(ref['menu']);
      
      if ('tab' in ref) {
        open_tab(ref['tab']);
      }

      if ('anchor' in ref) {
        open_doc(ref['doc'], ref['anchor']);
      } else {
        open_doc(ref['doc']);
      }
    });

  });
}
