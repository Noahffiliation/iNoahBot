module.exports = {
	name: 'server',
	description: 'Display info about this server.',
	guildOnly: true,
	execute(message) {
		const memberCount = message.guild.members.cache.filter(member => !member.user.bot).size;
		message.channel.send(`Server name: ${message.guild.name}\nTotal members: ${memberCount}`);
	},
};