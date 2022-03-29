function add_variant() {
  'use_strict'
  let fields_count = Number(count.innerHTML)
  let new_input =  document.createElement('input')
  new_input.name = `add_answer_${fields_count}`
  new_input.required = true
  new_input.style.marginTop = '3px'
  new_input.classList.add('styled-text-input');
  new_input.id = `add_answer_${fields_count}`
  variants_container.appendChild(new_input)
  new_input.focus()

  count.innerHTML = String(fields_count+1)
}
