module.exports = {
	name: 'server',
	description: 'Display info about this server.',
	aliases: ['serverinfo', 'guildinfo', 'guild'],
	usage: '[command name]',
	cooldown: 5,
	guildOnly: true,
	args: false,
	execute(message) {
		// Check if user is a mod or me
		if (message.member.roles.cache.has('450162671204171776') || message.member.roles.cache.has('421718388830765058')) message.channel.send(`Server name: ${message.guild.name}\nDescription: ${message.guild.description}\nOwner: ${message.guild.owner}\nRegion: ${message.guild.region}\nFeatures: ${message.guild.features}\nTotal members: ${message.guild.memberCount}\nTotal roles: ${message.guild.roles.cache.size}\nTotal emojis: ${message.guild.emojis.cache.size}\n`);
		else message.reply('You\'re not a mod!');
	},
};