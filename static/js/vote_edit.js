function add_variant() {
  'use_strict'
  let fields_count = Number(count.innerHTML)
  let new_input =  document.createElement('input')
  let new_save = document.createElement('button')
  let new_delete = document.createElement('button')
  new_input.name = `add_answer_${fields_count}`
  new_input.required = true
  new_input.type = "text"
  new_input.style.width = "65%"
  new_input.classList.add('form-control', 'mt-3', 'mx-2', 'me-3');
  new_input.id = `add_answer`

  new_delete.classList.add('btn', 'btn-danger', 'mx-auto', 'mt-3');
  new_delete.type = "submit"
  new_delete.style.width = "7%"
  new_delete.style.height = "3%"
  new_delete.id = `delete_var`

  new_save.classList.add('btn', 'btn-warning', 'mx-auto', 'mt-3');
  new_save.type = "submit"
  new_save.style.width = "6%"
  new_save.style.height = "3%"
  new_save.id = `save_var`

  let delete_icon = document.createElement('i')
  delete_icon.classList.add('bi', 'bi-trash-fill');
  let save_icon = document.createElement('i')
  save_icon.classList.add('bi', 'bi-cloud-plus-fill');

  variants_container.appendChild(new_input)
  variants_container.appendChild(new_save)
  save_var.appendChild(save_icon)
  variants_container.appendChild(new_delete)
  delete_var.appendChild(delete_icon)

  new_input.focus()

  count.innerHTML = String(fields_count+1)
}
