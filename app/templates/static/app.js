const deleteButtonIndex = "delete-task";
const taskRowIndex = "task-row-";

class Template {
      constructor(template) {
		this.addButton = document.getElementById("add-task");
            this.nameElement = document.getElementById("name");
            this.descriptionElement = document.getElementById("description");
            this.statusElement = document.getElementById("status");
            this.tasksTableElement = document.getElementById("tasks-table");
            this.weatherElement = document.getElementById("weather");
	} 

      addTask(task){
            return `<tr id="${taskRowIndex}${task.id}">
            <td>${task.id}</td>
            <td>${task.name}</td>
            <td>${task.description}</td>
            <td>${task.status}</td>
            <td><button class="${deleteButtonIndex}" value="${task.id}" type="button">Delete</button></td>
          </tr>`;
      }

      addWeather(data){
            return `<p>${data["description"]} ${data["temperature"]}</p>`
      }

}

class View {
      constructor(template) {
		this.template = template;
	}

      addTaskEvent(callback){
            this.template.addButton.addEventListener("click", callback);
      }

      deleteTaskEvent(callback, id){
            console.log("deleteTaskEvent "+deleteButtonIndex +" " +id);
            const buttons = document.getElementsByClassName(deleteButtonIndex);
            for (let i = 0; i < buttons.length; i++) {
                  const button = buttons[i];
                  button.addEventListener("click", callback);
            }
      }

      getGeolocationEvent(callback){
            document.addEventListener("DOMContentLoaded", callback);
      }

      getNewTaskData(){
            return {
                  name: this.template.nameElement.value,
                  description: this.template.descriptionElement.value,
                  status: this.template.statusElement.value
            }
      }

      clearTaskData(){
            this.template.nameElement.value = "";
            this.template.descriptionElement.value = "";
      }

      addTask(task){
            this.template.tasksTableElement.innerHTML += this.template.addTask(task);
      }

      addWeather(data){
            this.template.weatherElement.innerHTML += this.template.addWeather(data);
      }
}

class Store {
	
	constructor() {
            this.url = "/tasks";
            this.weather_url = "/weather";
	}

      async getWeather(latitude, longitude){
            const method = "GET";
            const url = this.weather_url + `?latitude=${latitude}&longitude=${longitude}`
            const response = await fetch(url, {method});
            await this._logProcessTime(response, method);
            return await response.json();
      }

      async getTasks(){
            const method = "GET";
            const response = await fetch(this.url, {method});
            await this._logProcessTime(response, method);
            const tasks = await response.json();
            return tasks
      }

      async addTask(task){
            const method = "POST"
            const response = await fetch(
                  this.url,
                  {
                        method,
                        body: JSON.stringify(task),
                        headers: {
                              "Content-Type": "application/json",
                        },
                  });
            await this._logProcessTime(response, method);
            const taskResponce = await response.json();
            return taskResponce
      }

      async deleteTask(id){
            const method = "DELETE"
            const response = await fetch(this.url+"/"+id, {method})
            await this._logProcessTime(response, method);
      }

      async _logProcessTime(response, method) {
            const processTime = await response.headers.get('X-Process-Time');
            console.table(method, response.url, processTime);
            const timeTable = document.getElementById("time-table");
            let style = "";
            if (processTime > 500){
                  style = 'style="background-color: brown;"';
            }
            timeTable.innerHTML += `<tr ${style}>
            <td>${method}</td>
            <td>${response.url}</td>
            <td>${processTime}</td>
          </tr>`;
      }
}

class TestStore {
	
	constructor() {
		this.tasks = [
                  {
                        description: "wqwqw",
                        id: 1,
                        name: "qwq",
                        status: "completed"
                  },
            ];
	}

      async getTasks(){
            return this.tasks
      }

      async addTask(task){
            task["id"]=this.tasks.length+1;
            this.tasks.push(task);
            return task
      }

      async deleteTask(id){
            this.tasks = this.tasks.filter((task) => task.id !== parseInt(id))
      }

      async getWeather(latitude, longitude){
            return {
                  "description": "overcast clouds",
                  "temperature": 298.42
            }
      }
}

class Controller {

	constructor(store, view) {
		this.store = store;
		this.view = view;
            
            this.deleteItem = this.deleteItem.bind(this)
		view.addTaskEvent(this.addTask.bind(this));
            view.getGeolocationEvent(this.getGeolocation.bind(this))
            Promise.resolve(store.getTasks())
            .then((tasks) => {
                  for (const index in tasks){
                        const task = tasks[index]
                        this.view.addTask(task);
                        this.view.deleteTaskEvent(this.deleteItem, task.id);
                  }
            });
	}

	addTask(event) {
            const task = this.view.getNewTaskData();
            
            Promise.resolve(this.store.addTask(task))
            .then((task) => {
                  this.view.clearTaskData();
                  this.addTaskItem(task)
            });
	}

      addTaskItem(task){
            this.view.addTask(task);
            this.view.deleteTaskEvent(this.deleteItem, task.id);
      }

      deleteItem(event) {
            const id = event.target.value;
            Promise.resolve(this.store.deleteTask(id))
            .then(() => {
                  document.getElementById(taskRowIndex + id).remove();
                  console.log("deleteItem "+id);
            });
            
      }

      getGeolocation(){
            if (navigator.geolocation) {
                  navigator.geolocation.getCurrentPosition(this.processGeolocation.bind(this));
            } else {
                  console.info("Geolocation is not supported by this browser.");
            }
      }

      processGeolocation(position){
            console.info("processGeolocation");
            console.log(
                  "Latitude: " + position.coords.latitude +
                  " Longitude: " + position.coords.longitude
            );
            Promise.resolve(this.store.getWeather(
                  position.coords.latitude,
                  position.coords.longitude
            ))
            .then((data) => {
                  this.view.addWeather(data);
            });
      }
}

//const store = new TestStore();
const store = new Store();

const template = new Template();
const view = new View(template);

const controller = new Controller(store, view);
