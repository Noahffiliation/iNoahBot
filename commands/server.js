module.exports = {
	name: 'server',
	description: 'Display info about this server.',
	guildOnly: true,
	execute(message) {
		// Returns total number of members with bots not included
		const memberCount = message.guild.members.cache.filter(member => !member.user.bot).size;
		message.channel.send(`Server name: ${message.guild.name}\nTotal members: ${memberCount}`);
	},
};