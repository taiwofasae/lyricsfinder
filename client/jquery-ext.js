/* 
 * Return outerHTML for the first element in a jQuery object,
 * or an empty string if the jQuery object is empty;  
 */
jQuery.fn.outerHTML = function() {
   return (this[0]) ? this[0].outerHTML : '';  
};