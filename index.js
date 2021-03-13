const Discord = require('discord.js');
const fs = require('fs');
const winston = require('winston');
const { prefix, token } = require('./config.json');

// Set main client and helper collections
const client = new Discord.Client();
client.commands = new Discord.Collection();
const cooldowns = new Discord.Collection();

// Build the array of commands from the commands folder
const commandFiles = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));
for (const file of commandFiles) {
	const command = require(`./commands/${file}`);
	client.commands.set(command.name, command);
}

// Create logger
const logger = winston.createLogger({
	transports: [
		new winston.transports.Console(),
		new winston.transports.File({ filename: './logs/log.log' }),
		new winston.transports.File({ filename: './logs/error.log', level: 'error' }),
	],
	format: winston.format.combine(
		winston.format.timestamp({
			format: 'YYYY-MM-DD HH:mm:ss',
		}),
		winston.format.printf(log => `${log.timestamp} - [${log.level.toUpperCase()}] - ${log.message}`),
	),
});

// On startup
client.once('ready', () => {
	logger.log('info', 'iNoahBot is online!');
	client.user.setActivity('myself get coded', { type: 'WATCHING' })
		.then(presence => logger.log('info', `Activity set to: ${presence.activities[0].type} ${presence.activities[0].name}`))
		.catch(console.error);
});

// On adding a user
client.on('guildMemberAdd', member => {
	logger.log('info', `${member} has joined the server`);
});

// On removing a user
client.on('guildMemberRemove', member => {
	logger.log('info', `${member} has left the server`);
});

// On getting a message
client.on('message', message => {
	// Make sure the message starts with a command and not from a bot
	if (!message.content.startsWith(prefix) || message.author.bot) return;

	// Split into the command and its arguments
	const args = message.content.slice(prefix.length).trim().split(/ +/);
	const commandName = args.shift().toLowerCase();

	// Find aliases
	const command = client.commands.get(commandName) || client.commands.find(cmd => cmd.aliases && cmd.aliases.includes(commandName));

	if (!command) return;

	// Check for guild-only commands
	if (command.guildOnly && message.channel.type === 'dm') {
		return message.reply('I can\'t execute that command inside DMs!');
	}

	// Check for arguments
	if (command.args && !args.length) {
		let reply = `You didn't provide any arguments, ${message.author}!`;

		if (command.usage) {
			reply += `\nThe proper usage would be: \`${prefix}${command.name} ${command.usage}\``;
		}

		return message.channel.send(reply);
	}

	// Put command in cooldown
	if (!cooldowns.has(command.name)) {
		cooldowns.set(command.name, new Discord.Collection());
	}

	const now = Date.now();
	const timestamps = cooldowns.get(command.name);

	// Use command's cooldown or default of 3 seconds
	const cooldownAmount = (command.cooldown || 3) * 1000;

	// Add cooldown time to command
	if (timestamps.has(message.author.id)) {
		const expirationTime = timestamps.get(message.author.id) + cooldownAmount;

		// Calculate cooldown time left
		if (now < expirationTime) {
			const timeLeft = (expirationTime - now) / 1000;
			return message.reply(`please wait ${timeLeft.toFixed(1)} more second(s) before reusing the \`${command.name}\` command.`);
		}
	}

	// Remove command from cooldown collection when ready
	timestamps.set(message.author.id, now);
	setTimeout(() => timestamps.delete(message.author.id), cooldownAmount);

	// Execute the command
	try {
		command.execute(message, args);
	}
	catch (error) {
		console.error(error);
		logger.log('error', error);
		message.reply('there was an error trying to execute that command!');
	}
});

// Log errors
client.on('error', error => {
	console.error(error);
	logger.log('error', error);
});
process.on('uncaughtException', error => logger.log('error', error));

client.login(token);