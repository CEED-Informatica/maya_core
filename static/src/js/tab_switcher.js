
/** @odoo-module **/

/**
 * @odoo-module
 * Permite indicarle:
 * - Es un módulo compatible con Owl / ES modules
 * - Debe ser procesado por el module loader de Odoo
 * - Puede usar import y export
 * - Debe cargar dentro del sistema modular de Odoo
*/

/**
 * Permite cambiar de pestaña via código
 */

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { onMounted } from "@odoo/owl";

patch(FormController.prototype, {

  setup(...args) {
    // Llamada al setup original
    super.setup();

    // Registro los eventos una vez esté montado el DOM
    onMounted(() => {
        console.warn("onMounted → DOM listo, registrando tab switcher");
        this._registerTabEvents(this.__owl__.bdom.el);

    });
  }, 

  _registerTabEvents(el) {
    
    if (!el) {
      console.warn("FormController.__owl__.bdom.el NO está disponible");
      return;
    }
    
    // Evita múltiples registros
    if (el._maya_tab_switcher_registered) {
      return;
    }
    el._maya_tab_switcher_registered = true;

    el.addEventListener("click", (ev) => {

      const button = ev.target.closest("a.o_internal_tab_switcher");
      if (!button) return;

      const targetTab = button.dataset.targetTabName;
      if (!targetTab) return;
    
      const notebookEl = this.__owl__.bdom.el.querySelector("div.o_notebook_headers"); 
      if (!notebookEl) {
        console.error("No se encuentra el contenedor de la notebook");
        return;
      }

      // Busca el enlace de la pestaña por name
      const tabLink = notebookEl.querySelector(`.nav-link[name="${targetTab}"]`);

      if (!tabLink) {
        console.warn("No se encuentra la pestaña:", targetTab);
        return;
      }

      try {
        console.warn(`Simulando click en tab: ${targetTab}`);
        tabLink.click(); // Simulo el click
      } catch (err) {
        console.error("Error al simular el click de la pestaña:", err);
      }
    });
  },
});
