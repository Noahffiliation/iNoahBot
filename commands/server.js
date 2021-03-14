module.exports = {
	name: 'server',
	description: 'Display info about this server.',
	aliases: ['serverinfo', 'guildinfo', 'guild'],
	usage: '[command name]',
	cooldown: 5,
	guildOnly: true,
	args: false,
	execute(message) {
		message.channel.send(`Server name: ${message.guild.name}\nDescription: ${message.guild.description}\nOwner: ${message.guild.owner}\nRegion: ${message.guild.region}\nFeatures: ${message.guild.features}\nTotal members: ${message.guild.memberCount}\nTotal roles: ${message.guild.roles.cache.size}\nTotal emojis: ${message.guild.emojis.cache.size}\n`);
	},
};